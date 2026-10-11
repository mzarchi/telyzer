use crate::error::{CoreError, Result};
use directories::ProjectDirs;
use std::fs;
use std::path::{Path, PathBuf};

const QUALIFIER: &str = "com";
const ORGANIZATION: &str = "";
const APPLICATION: &str = "telyzer";

#[derive(Debug, Clone)]
pub struct Paths {
    data_dir: PathBuf,
    config_dir: PathBuf,
}

impl Paths {
    pub fn init() -> Result<Self> {
        let proj_dirs = ProjectDirs::from(QUALIFIER, ORGANIZATION, APPLICATION)
            .ok_or(CoreError::ProjectDirsUnavailable)?;

        let data_dir = proj_dirs.data_dir().to_path_buf();
        let config_dir = proj_dirs.config_dir().to_path_buf();

        ensure_dir(&data_dir)?;
        ensure_dir(&config_dir)?;

        Ok(Self {
            data_dir,
            config_dir,
        })
    }

    pub fn data_dir(&self) -> &Path {
        &self.data_dir
    }

    pub fn config_dir(&self) -> &Path {
        &self.config_dir
    }

    pub fn session_file(&self) -> PathBuf {
        self.data_dir.join("session.sqlite")
    }

    pub fn config_file(&self) -> PathBuf {
        self.config_dir.join("config.toml")
    }
}

fn ensure_dir(path: &Path) -> Result<()> {
    if path.exists() {
        return Ok(());
    }

    fs::create_dir_all(path).map_err(|source| CoreError::CreateDir {
        path: path.display().to_string(),
        source,
    })?;

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let perms = fs::Permissions::from_mode(0o700);
        let _ = fs::set_permissions(path, perms);
    }

    Ok(())
}
