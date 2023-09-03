import json
from models.simulation import Simulation  # Ajuste o import conforme sua estrutura de pastas

if __name__ == "__main__":
    # Carregar configurações do arquivo JSON.
    with open('../config.json', 'r') as f:  # Ajuste o caminho conforme sua estrutura de pastas
        config = json.load(f)

    # Criar uma instância da classe Simulation.
    sim = Simulation(config)

    # Definir o período de tempo para a simulação.
    sim.set_time_period(months=1)

    # Executar a simulação.
    sim.run_simulation()

    # Exportar os dados para um arquivo CSV.
    sim.export_to_csv("output.csv")
