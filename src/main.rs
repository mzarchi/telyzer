mod app;
mod constants;
mod ui;

use app::LoginApp;
use constants::*;

fn main() -> iced::Result {
    iced::application(
        LoginApp::new,
        LoginApp::update,
        ui::view,
    )
    .title(TITLE)
    .window_size((WINDOW_WIDTH, WINDOW_HEIGHT))
    .run()
}