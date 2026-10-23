use anyhow::Result;
use telyzer_core::TelyzerClient;

pub async fn run(client: &TelyzerClient) -> Result<()> {
    if !client.is_authorized().await? {
        println!("Not logged in. Use 'Login' first.");
        return Ok(());
    }

    let me = client.get_me().await?;
    println!("Name:     {}", me.first_name().unwrap_or("(no name)"));
    println!("ID:       {}", me.id());
    println!("Username: @{}", me.username().unwrap_or("(none)"));
    println!("Phone:    {}", me.phone().unwrap_or("(hidden)"));

    Ok(())
}
