//! The built executable exports the symbols that make D3D12 load the Agility SDK in `D3D12\`
//! (issues #11, #85: without them Windows 10's in-box runtime refuses our root signatures).
#![cfg(all(windows, target_env = "msvc"))]

#[test]
fn executable_exports_the_agility_sdk_symbols() {
    let data = std::fs::read(env!("CARGO_BIN_EXE_victory")).unwrap();
    let image = victory_pe::ImageInfo::parse(&data).unwrap();
    for wanted in ["D3D12SDKVersion", "D3D12SDKPath"] {
        assert!(
            image.exports.iter().any(|e| e.name.as_deref() == Some(wanted)),
            "victory.exe does not export {wanted}"
        );
    }
}
