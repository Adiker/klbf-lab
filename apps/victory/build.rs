//! Exports the two symbols by which the D3D12 loader finds the redistributable runtime (Agility
//! SDK) in `D3D12\` beside the executable. Without them, Windows 10's in-box D3D12 is used and it
//! refuses our root signature flags.
fn main() {
    if std::env::var("CARGO_CFG_TARGET_ENV").is_ok_and(|v| v == "msvc") {
        println!("cargo:rustc-link-arg-bins=/EXPORT:D3D12SDKVersion,DATA");
        println!("cargo:rustc-link-arg-bins=/EXPORT:D3D12SDKPath,DATA");
    }
}
