use eframe::egui;
use crate::app::LoginApp;
use crate::constants::*;

pub fn draw_login(ui: &mut egui::Ui, app: &mut LoginApp) {
    ui.vertical_centered(|ui| {
        ui.add_space(SPACE_TOP);
        draw_title(ui);
        ui.add_space(SPACE_AFTER_TITLE);
        draw_phone_input(ui, app);
        ui.add_space(SPACE_BEFORE_BUTTON);
        draw_login_button(ui, app);
        draw_error(ui, app);
    });
}

fn draw_title(ui: &mut egui::Ui) {
    ui.label(egui::RichText::new(TITLE).size(FONT_TITLE).strong());
}

fn draw_phone_input(ui: &mut egui::Ui, app: &mut LoginApp) {
    ui.label(egui::RichText::new(LABEL_PHONE).size(FONT_LABEL));
    ui.add_space(6.0);
    ui.add_sized(
        [INPUT_WIDTH, INPUT_HEIGHT],
        egui::TextEdit::singleline(&mut app.phone)
            .font(egui::TextStyle::Body)
            .hint_text("0912..."),
    );
}

fn draw_login_button(ui: &mut egui::Ui, app: &mut LoginApp) {
    let button = egui::Button::new(
        egui::RichText::new(BUTTON_LOGIN).size(FONT_BUTTON),
    )
    .min_size(egui::vec2(BUTTON_WIDTH, BUTTON_HEIGHT));

    if ui.add(button).clicked() {
        app.try_login();
    }
}

fn draw_error(ui: &mut egui::Ui, app: &LoginApp) {
    if let Some(msg) = &app.error {
        ui.add_space(SPACE_BETWEEN_FIELDS);
        ui.colored_label(egui::Color32::RED, msg);
    }
}