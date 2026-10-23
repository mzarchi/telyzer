use crate::error::{CoreError, Result};
use directories::ProjectDirs;
use std::fs;
use std::io;
use std::path::{Path, PathBuf};

const QUALIFIER: &str = "com";
const ORGANIZATION: &str = "";
const APPLICATION: &str = "telyzer";

const SESSION_FILE: &str = "session.sqlite";
// SQLite side files that live next to the session database
const SESSION_SUFFIXES: [&str; 4] = ["", "-wal", "-shm", "-journal"];

#[derive(Debug, Clone)]
pub struct Paths {
    data_dir: PathBuf,
}

impl Paths {
    pub fn init() -> Result<Self> {
        let proj_dirs = ProjectDirs::from(QUALIFIER, ORGANIZATION, APPLICATION)
            .ok_or(CoreError::ProjectDirsUnavailable)?;
        Self::from_dir(proj_dirs.data_dir().to_path_buf())
    }

    /// Creates `Paths` rooted at an explicit directory (used by tests).
    pub fn from_dir(data_dir: PathBuf) -> Result<Self> {
        ensure_dir(&data_dir)?;
        Ok(Self { data_dir })
    }

    pub fn data_dir(&self) -> &Path {
        &self.data_dir
    }

    pub fn session_file(&self) -> PathBuf {
        self.data_dir.join(SESSION_FILE)
    }

    /// Makes sure the session file exists and is private (0600 on Unix)
    /// *before* SQLite opens it, so it is never created world-readable.
    pub fn prepare_session_file(&self) -> Result<PathBuf> {
        let path = self.session_file();
        create_private_file(&path)?;
        Ok(path)
    }

    /// Deletes the session file and its SQLite side files. Missing files are fine.
    pub fn remove_session_files(&self) -> Result<()> {
        let base = self.session_file();
        for suffix in SESSION_SUFFIXES {
            let mut os = base.clone().into_os_string();
            os.push(suffix);
            let path = PathBuf::from(os);

            match fs::remove_file(&path) {
                Ok(()) => {}
                Err(e) if e.kind() == io::ErrorKind::NotFound => {}
                Err(source) => {
                    return Err(CoreError::RemoveFile {
                        path: path.display().to_string(),
                        source,
                    })
                }
            }
        }
        Ok(())
    }
}

fn ensure_dir(path: &Path) -> Result<()> {
    fs::create_dir_all(path).map_err(|source| CoreError::CreateDir {
        path: path.display().to_string(),
        source,
    })?;
    // Always applied, not only when the directory was just created
    restrict(path, 0o700)
}

fn create_private_file(path: &Path) -> Result<()> {
    let mut options = fs::OpenOptions::new();
    options.create(true).append(true);

    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        options.mode(0o600);
    }

    options.open(path).map_err(|source| CoreError::CreateFile {
        path: path.display().to_string(),
        source,
    })?;

    // Fixes the mode if the file already existed with looser permissions
    restrict(path, 0o600)
}

#[cfg(unix)]
fn restrict(path: &Path, mode: u32) -> Result<()> {
    use std::os::unix::fs::PermissionsExt;
    fs::set_permissions(path, fs::Permissions::from_mode(mode)).map_err(|source| {
        CoreError::SetPermissions {
            path: path.display().to_string(),
            source,
        }
    })
}

// On Windows the per-user AppData directory is private by default
#[cfg(not(unix))]
fn restrict(_path: &Path, _mode: u32) -> Result<()> {
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[cfg(unix)]
    fn mode(path: &Path) -> u32 {
        use std::os::unix::fs::PermissionsExt;
        fs::metadata(path).unwrap().permissions().mode() & 0o777
    }

    #[test]
    fn session_file_is_inside_data_dir() {
        let tmp = tempfile::tempdir().unwrap();
        let paths = Paths::from_dir(tmp.path().join("data")).unwrap();
        assert_eq!(paths.session_file(), tmp.path().join("data/session.sqlite"));
    }

    #[test]
    fn from_dir_creates_nested_directories() {
        let tmp = tempfile::tempdir().unwrap();
        let nested = tmp.path().join("a/b/c");
        Paths::from_dir(nested.clone()).unwrap();
        assert!(nested.is_dir());
    }

    #[cfg(unix)]
    #[test]
    fn new_dir_and_session_file_are_private() {
        let tmp = tempfile::tempdir().unwrap();
        let paths = Paths::from_dir(tmp.path().join("data")).unwrap();
        let file = paths.prepare_session_file().unwrap();

        assert_eq!(mode(paths.data_dir()), 0o700);
        assert_eq!(mode(&file), 0o600);
    }

    #[cfg(unix)]
    #[test]
    fn existing_loose_permissions_are_tightened() {
        use std::os::unix::fs::PermissionsExt;

        let tmp = tempfile::tempdir().unwrap();
        let dir = tmp.path().join("data");
        fs::create_dir(&dir).unwrap();
        fs::set_permissions(&dir, fs::Permissions::from_mode(0o755)).unwrap();
        let file = dir.join("session.sqlite");
        fs::write(&file, b"").unwrap();
        fs::set_permissions(&file, fs::Permissions::from_mode(0o644)).unwrap();

        let paths = Paths::from_dir(dir.clone()).unwrap();
        paths.prepare_session_file().unwrap();

        assert_eq!(mode(&dir), 0o700);
        assert_eq!(mode(&file), 0o600);
    }

    #[test]
    fn prepare_does_not_truncate_existing_session() {
        let tmp = tempfile::tempdir().unwrap();
        let paths = Paths::from_dir(tmp.path().join("data")).unwrap();
        fs::write(paths.session_file(), b"keep me").unwrap();

        paths.prepare_session_file().unwrap();

        assert_eq!(fs::read(paths.session_file()).unwrap(), b"keep me");
    }

    #[test]
    fn remove_session_files_deletes_all_and_is_idempotent() {
        let tmp = tempfile::tempdir().unwrap();
        let paths = Paths::from_dir(tmp.path().join("data")).unwrap();
        let base = paths.session_file();
        for suffix in SESSION_SUFFIXES {
            let mut os = base.clone().into_os_string();
            os.push(suffix);
            fs::write(PathBuf::from(os), b"x").unwrap();
        }

        paths.remove_session_files().unwrap();
        assert!(!base.exists());
        assert!(!tmp.path().join("data/session.sqlite-wal").exists());

        // A second call must not fail
        paths.remove_session_files().unwrap();
    }
}
