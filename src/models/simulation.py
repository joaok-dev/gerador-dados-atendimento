import random
from datetime import datetime, timedelta
from .tickets import ticket 


class Simulation:
    def __init__(self, config):
        """
        Initialize a new Simulation object.

        :param config: Dictionary containing simulation settings like operation 
        type, working hours, etc.
        """
        self.tickets = []
        self.config = config


    def generate_ticket(self):
        """
        Generates a random ticket based on the simulation settings and adds it to 
        the tickets list.
        """
        # Gerar um ID único para a chamada (usando o tamanho atual da lista `tickets`)
        ticket_id = len(self.tickets) + 1

        # Gera uma data e hora aleatórias dentro do intervalo entre start_date e end_date.
        random_date = self.start_date + (self.end_date - self.start_date) * random.random()
        
        # Atribui a data e hora aleatórias geradas ao horário de início do ticket.
        start_time = random_date
        
        # Gera um horário de término para o ticket, que é um valor aleatório de 1 a 10 minutos após o horário de início.
        end_time = start_time + timedelta(minutes=random.randint(1, 10))
        
        # Seleciona aleatoriamente um tipo para o ticket de uma lista de tipos possíveis.
        ticket_type = random.choice(["voice", "chat", "email"])
        
        # Cria um novo objeto Ticket com os valores gerados.
        new_ticket = Ticket(ticket_id, start_time, end_time, ticket_type)
        
        # Adiciona o novo objeto Ticket à lista de tickets.
        self.tickets.append(new_ticket)

    
    def set_time_period(self, months=None, start_date=None, end_date=None):
        """
        Set the time period for the simulation.
        
        :param months: Number of months to go back from today.
        :param start_date: Specific start date for the simulation.
        :param end_date: Specific end date for the simulation.
        """
        today = datetime.now()
        
        if months:
            self.start_date = today - timedelta(days=30 * months)
            self.end_date = today
        elif start_date and end_date:
            # Converte as datas de string para objeto datetime, se necessário
            self.start_date = datetime.strptime(start_date, '%Y-%m-%d') if isinstance(start_date, str) else start_date
            self.end_date = datetime.strptime(end_date, '%Y-%m-%d') if isinstance(end_date, str) else end_date
        else:
            raise ValueError("Either 'months' or 'start_date and end_date' must be provided.")


    def run_simulation(self):
        """
        Executes the simulation by generating tickets and populating the tickets list.
        """
        # Determinar o número total de dias no intervalo de simulação.
        total_days = (self.end_date - self.start_date).days
        
        # Suponhamos que o volume médio diário de tickets seja fornecido nas configurações.
        average_daily_volume = self.config["average_daily_volume"]
        
        # Calcular o número total de tickets a serem gerados.
        total_tickets = total_days * average_daily_volume
        
        # Executar um loop para gerar o número total de tickets.
        for i in range(total_tickets):
            self.generate_ticket()
            
        # Aqui, você pode adicionar lógica adicional para simular variações no volume de tickets.

    def export_to_csv(self):
        """
        Exports the generated tickets to a CSV file.
        """
        pass  # To be implemented
