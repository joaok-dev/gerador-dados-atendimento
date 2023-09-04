import typer
import json
import sys
from datetime import datetime
from models.simulation import Simulation

app = typer.Typer()

def print_colored_line(line, colors):
    segment_length = len(line) // len(colors)
    for i in range(len(colors)):
        start = i * segment_length
        end = (i + 1) * segment_length
        typer.secho(line[start:end], fg=colors[i], nl=False)
    typer.echo("")
    

def print_welcome_message():
    typer.echo("\n\n\n")
    lines = [
         "██████╗ ██╗      █████╗ ███╗   ██╗███████╗     ██╗ █████╗ ███╗   ███╗███████╗███╗   ██╗████████╗ ██████╗",
        "██╔══██╗██║     ██╔══██╗████╗  ██║██╔════╝     ██║██╔══██╗████╗ ████║██╔════╝████╗  ██║╚══██╔══╝██╔═══██╗",
        "██████╔╝██║     ███████║██╔██╗ ██║█████╗       ██║███████║██╔████╔██║█████╗  ██╔██╗ ██║   ██║   ██║   ██║",
        "██╔═══╝ ██║     ██╔══██║██║╚██╗██║██╔══╝  ██   ██║██╔══██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║   ██║   ██║",
        "██║     ███████╗██║  ██║██║ ╚████║███████╗╚█████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║ ╚████║   ██║   ╚██████╔╝",
        "╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝ ╚════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ "
    ]
    colors = [typer.colors.RED, typer.colors.GREEN, typer.colors.YELLOW, typer.colors.BLUE, typer.colors.MAGENTA, typer.colors.CYAN, typer.colors.WHITE, typer.colors.BRIGHT_GREEN]
    for line in lines:
        print_colored_line(line, colors)
    typer.echo("\n\n\n")
    typer.secho("Bem-vindo ao Simulador de Atendimento!", fg=typer.colors.GREEN, bold=True)
    typer.secho("Este programa simula o atendimento ao cliente com base nas configurações que você fornecer.", fg=typer.colors.BLUE)
    typer.secho("Para sair do programa a qualquer momento, pressione 'Ctrl+C'.", fg=typer.colors.RED)
    typer.secho("Pressione [Enter] para continuar...", fg=typer.colors.YELLOW)
    input()

def validate_input(prompt, validation_func=None):
    while True:
        try:
            user_input = typer.prompt(prompt)
            if validation_func:
                if not validation_func(user_input):
                    raise ValueError("Entrada inválida.")
            return user_input
        except KeyboardInterrupt:
            typer.secho("\nOperação interrompida pelo usuário. Até mais!", fg=typer.colors.YELLOW)
            sys.exit(0)
        except ValueError as ve:
            typer.secho(f"Erro: {ve}. Tente novamente.", fg=typer.colors.RED)


def validate_choice(prompt, options):
    while True:
        try:
            choice = int(typer.prompt(prompt))
            if choice not in options:
                raise ValueError("Opção inválida. Por favor, escolha um número da lista.")
            return choice
        except KeyboardInterrupt:
            typer.secho("\nOperação interrompida pelo usuário. Até mais!", fg=typer.colors.YELLOW)
            sys.exit(0)
        except ValueError as ve:
            typer.secho(f"Erro: {ve}. Tente novamente.", fg=typer.colors.RED)


def get_user_choice(prompt, options):
    typer.echo(prompt)
    for key, (_, desc) in options.items():
        typer.echo(f"{key}: {desc}")
        
    choice = validate_input("\nDigite o número da sua escolha: ", lambda x: int(x) in options.keys())
    return options[int(choice)][0]

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def choose_operation_size():
    return get_user_choice(
        "Escolha o tamanho da operação:",
        {
            1: ("very_small", "Operação muito pequena"),
            2: ("small", "Operação pequena"),
            3: ("medium", "Operação média"),
            4: ("large", "Operação grande"),
            5: ("very_large", "Operação muito grande")
        }
    )

def choose_dates():
    choice = get_user_choice(
        "Escolha o período de simulação:",
        {
            1: ("start_end_dates", "Especificar datas de início e término"),
            2: ("months_from_today", "Especificar o número de meses a partir de hoje")
        }
    )
    
    if choice == 'start_end_dates':
        start_date = validate_input("Data de início (DD/MM/AAAA): ", is_valid_date)
        end_date = validate_input("Data de término (DD/MM/AAAA): ", is_valid_date)
        return start_date, end_date, None
    else:
        months = validate_input("Número de meses a partir de hoje: ", lambda x: x.isdigit())
        return None, None, int(months)


@app.command()
def main():
    try:
        print_welcome_message()
        operation_size = choose_operation_size()
        start_date, end_date, months = choose_dates()

        with open("../config.json", "r") as f:
            config = json.load(f)

        new_config = {"default": {"size_profile": operation_size}}
        sim = Simulation(config)
        sim.update_config(new_config)

        if start_date and end_date:
            sim.set_time_period(start_date=start_date, end_date=end_date)
        elif months:
            sim.set_time_period(months=months)

        sim.run_simulation()
        sim.export_to_csv()

        typer.echo("")
        typer.secho("Simulação concluída com sucesso!", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"O arquivo CSV foi salvo em /data_out.")

    except KeyboardInterrupt:
        typer.secho("\nOperação interrompida pelo usuário. Até mais!", fg=typer.colors.YELLOW)
        sys.exit(0)

    except Exception as e:
        typer.secho(f"Um erro inesperado ocorreu: {e}", fg=typer.colors.RED)
        sys.exit(1)

    typer.secho("Obrigado por usar o Simulador de Atendimento. Até a próxima!", fg=typer.colors.GREEN)
    sys.exit(0)

if __name__ == "__main__":
    app()
