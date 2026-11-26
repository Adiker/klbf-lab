//! (Neptune) A fingerprint of the shader translator's sources, for the shader cache's key
//! (`shader_cache::build`): the cache then lives through every rebuild that leaves
//! `victory-shader` as it was.
use std::path::{Path, PathBuf};

fn walk(dir: &Path, files: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else { return };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            walk(&path, files);
        } else if path.extension().is_some_and(|x| x == "rs") {
            files.push(path);
        }
    }
}

/// "https://user:token@github.com/owner/repo.git" or "git@github.com:owner/repo.git" -> "owner/repo".
fn owner_repo(url: &str) -> Option<String> {
    let rest = url.trim().split_once("://").map_or(url.trim(), |(_, r)| r);
    // Drop "user:token@" (or "git@") before the host.
    let rest = match rest.split_once('@') {
        Some((who, after)) if !who.contains('/') => after,
        _ => rest,
    };
    let path = rest.replace(':', "/");
    let mut parts = path.trim_end_matches('/').trim_end_matches(".git").rsplit('/');
    let repo = parts.next().filter(|s| !s.is_empty())?;
    let owner = parts.next().filter(|s| !s.is_empty())?;
    Some(format!("{owner}/{repo}"))
}

fn main() {
    let sources = Path::new(env!("CARGO_MANIFEST_DIR")).join("../victory-shader/src");
    let mut files = Vec::new();
    walk(&sources, &mut files);
    files.sort();
    // FNV-1a over every source file's bytes (line ends left out: a checkout's setting).
    let mut hash: u64 = 0xcbf2_9ce4_8422_2325;
    for file in &files {
        for byte in std::fs::read(file).unwrap_or_default() {
            if byte != b'\r' {
                hash = (hash ^ u64::from(byte)).wrapping_mul(0x0000_0100_0000_01b3);
            }
        }
    }
    println!("cargo:rustc-env=VICTORY_TRANSLATOR={hash:016x}-{}", files.len());
    println!("cargo:rerun-if-changed={}", sources.display());
    // The build tag: the git short hash (it moves with every commit through the log's file).
    let git = |args: &[&str]| {
        std::process::Command::new("git").args(args).output().ok().filter(|o| o.status.success()).map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
    };
    // (ours) Without git (the remote build gets `git archive`), compiler-distant.sh hands the
    // commit and the origin over as KLBF_GIT_SHA / KLBF_GIT_REMOTE.
    let env = |name: &str| std::env::var(name).ok().map(|v| v.trim().to_string()).filter(|v| !v.is_empty());
    let sha = git(&["rev-parse", "--short", "HEAD"]).or_else(|| env("KLBF_GIT_SHA"));
    println!("cargo:rustc-env=VICTORY_BUILD={}", sha.as_deref().unwrap_or("unknown"));
    if let Some(log) = git(&["rev-parse", "--git-path", "logs/HEAD"]) {
        println!("cargo:rerun-if-changed={log}");
    }
    // (ours) KLBF Lab Bench card: owner/repo from the origin (credentials never kept), else a
    // name declared with KLBF_PROJECT_NAME, else "unknown (local build)".
    let remote = git(&["remote", "get-url", "origin"]).or_else(|| env("KLBF_GIT_REMOTE"));
    let clean = |s: &str| s.chars().filter(|c| c.is_ascii_alphanumeric() || "-_./ ()".contains(*c)).take(80).collect::<String>();
    let (project, source) = match (remote.as_deref().and_then(owner_repo), env("KLBF_PROJECT_NAME")) {
        (Some(p), _) => (clean(&p), "git"),
        (None, Some(d)) => (clean(&d), "declared"),
        _ => ("unknown (local build)".to_string(), "none"),
    };
    println!("cargo:rustc-env=KLBF_PROJECT={project}");
    println!("cargo:rustc-env=KLBF_PROJECT_SOURCE={source}");
    println!("cargo:rustc-env=KLBF_SHA={}", sha.as_deref().map(clean).unwrap_or_else(|| "unknown".into()));
    for name in ["KLBF_GIT_SHA", "KLBF_GIT_REMOTE", "KLBF_PROJECT_NAME"] {
        println!("cargo:rerun-if-env-changed={name}");
    }
    println!("cargo:rerun-if-changed=build.rs");
}
