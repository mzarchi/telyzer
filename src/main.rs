mod app;
mod constants;
mod ui;

use app::LoginApp;
use constants::*;

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([WINDOW_WIDTH, WINDOW_HEIGHT])
            .with_min_inner_size([WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT]),
        ..Default::default()
    };

    eframe::run_native(
        "Telyzer",
        options,
        Box::new(|_cc| Ok(Box::new(LoginApp::new()))),
    )
}

impl eframe::App for LoginApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui::draw_login(ui, self);
        });
    }
}
