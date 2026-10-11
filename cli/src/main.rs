use anyhow::Result;

fn main() -> Result<()> {
    let paths = telyzer_core::Paths::init()?;
    println!("Data dir:   {}", paths.data_dir().display());
    println!("Config dir: {}", paths.config_dir().display());
    println!("Session:    {}", paths.session_file().display());
    Ok(())
}