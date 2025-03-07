from openai import OpenAI
from rich.console import Console
import os
from dotenv import load_dotenv

console = Console()

def test_openai_connection():
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable is not set[/red]")
        console.print("[yellow]Please set your OpenAI API key in the .env file[/yellow]")
        return
    
    try:
        # Create client
        client = OpenAI(api_key=api_key)
        
        # Make a simple API call
        console.print("\n[cyan]Testing OpenAI API connection...[/cyan]")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a known working model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Can you hear me? Please respond with 'Yes, I can hear you!'"}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        # Print the response
        console.print("\n[green]Success! OpenAI API is working.[/green]")
        console.print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        error_message = str(e)
        console.print(f"\n[red]Error: {error_message}[/red]")
        
        if "401" in error_message:
            console.print("[yellow]Invalid API key. Please check your key in the .env file.[/yellow]")
        elif "429" in error_message:
            console.print("[yellow]Rate limit exceeded. Please try again later.[/yellow]")
        elif "500" in error_message:
            console.print("[yellow]OpenAI server error. Please try again later.[/yellow]")
        else:
            console.print("[yellow]An unexpected error occurred. Please check your internet connection.[/yellow]")

if __name__ == "__main__":
    test_openai_connection() 