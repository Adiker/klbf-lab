// DirectX 12 Agility SDK: Windows loads D3D12Core.dll from .\D3D12\ next to
// the exe when it exports these two symbols (needed on Windows 10, whose
// built-in runtime lacks shader model 6.6 root signature flags).
fn main() {
    if std::env::var("CARGO_CFG_TARGET_OS").as_deref() == Ok("windows") {
        println!("cargo:rustc-link-arg-bins=/EXPORT:D3D12SDKVersion,DATA");
        println!("cargo:rustc-link-arg-bins=/EXPORT:D3D12SDKPath,DATA");
    }
}
