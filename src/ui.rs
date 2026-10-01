use iced::widget::{button, column, container, space, text, text_input};
use iced::{Element, Length};

use crate::app::{LoginApp, Message};
use crate::constants::*;

pub fn view(app: &LoginApp) -> Element<'_, Message> {
    let title = text(TITLE).size(FONT_TITLE);

    let phone_label = text(LABEL_PHONE).size(FONT_LABEL);

    let phone_input = text_input(HINT_PHONE, &app.phone)
        .on_input(Message::PhoneChanged)
        .on_submit(Message::LoginPressed)
        .padding(INPUT_PADDING)
        .size(FONT_INPUT);

    let login_button = button(text(BUTTON_LOGIN).size(FONT_BUTTON))
        .on_press(Message::LoginPressed);

    let mut content = column![
        space::vertical().height(SPACE_TOP),
        title,
        space::vertical().height(SPACE_AFTER_TITLE),
        phone_label,
        phone_input,
        space::vertical().height(SPACE_BEFORE_BUTTON),
        login_button,
    ]
    .spacing(SPACE_BETWEEN_FIELDS)
    .width(Length::Fixed(FORM_WIDTH))
    .align_x(iced::Alignment::Center);

    if let Some(error) = &app.error {
        content = content.push(text(error).size(FONT_LABEL).style(text::danger));
    }

    container(content)
        .center_x(Length::Fill)
        .center_y(Length::Fill)
        .into()
}