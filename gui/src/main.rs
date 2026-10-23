mod app;
mod constants;
mod ui;

use app::LoginApp;
use constants::TITLE;

pub fn main() -> iced::Result {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()),
        )
        .init();

    iced::application(TITLE, LoginApp::update, ui::view)
        .theme(|_| iced::Theme::Dark)
        .run()
}
