import json
import random
from datetime import datetime, timedelta
from .tickets import Ticket 


class Simulation:
    def __init__(self, config_file='config.json'):
        """
        Initialize a new Simulation object.

        :param config_file: String containing the path to the JSON config file.
        """
        # Carregar configurações do arquivo JSON.
        with open(config_file, 'r') as f:
            self.config = json.load(f)['default']
        # Lista para armazenar os tickets gerados.
        self.tickets = []

        self.weekly_volume = []
        

    def update_config(self, new_config):
        """
        Update the simulation settings.

        :param new_config: Dictionary containing new simulation settings.
        """
        # Atualizar as configurações com os novos valores fornecidos.
        self.config.update(new_config)

    
    def distribute_volume_among_weeks(self):
        """
        Distributes the average monthly volume of tickets among the weeks of the month.
    
        :param: None
        """
        avg_monthly_volume = self.config['average_monthly_volume']
        # Calculate the total number of days and weeks in the given time period
        total_days = (self.end_date - self.start_date).days
        full_weeks, extra_days = divmod(total_days, 7)
        # Allowed variation (in percentage) for distributing volume among weeks
        min_variation, max_variation = 23, 29  
        remaining_volume = avg_monthly_volume
        self.weekly_volume = []

        # Distribute volume among full weeks
        for i in range(full_weeks):
            min_allowed = int(avg_monthly_volume * min_variation / 100)
            max_allowed = int(avg_monthly_volume * max_variation / 100)
            week_volume = round(random.uniform(min_allowed, max_allowed), 2)
            remaining_volume -= week_volume
            self.weekly_volume.append(week_volume)

        # Distribute remaining volume among the extra days (if any)
        if extra_days > 0:
            extra_days_volume = remaining_volume * (extra_days / 7)
            self.weekly_volume.append(round(extra_days_volume, 2))

        else:
            # If there are no extra days, the remaining volume goes to the last full week.
            self.weekly_volume[-1] += remaining_volume



    def distribute_volume_among_days(self, week_volume):
        """
        Distributes the average weekly volume of tickets among the days of the week.

        :param week_volume: Total volume of tickets for the week.
        """
        # Definindo os perfis e seus pesos
        day_profiles = ['classic', 'weekend_heavy', 'midweek_peak', 'even_distribution', 'endweek_peak']
        weights = [0.4, 0.2, 0.15, 0.15, 0.1]
        chosen_day_profile = random.choices(day_profiles, weights=weights, k=1)[0]

        # Busca as proporções para o perfil escolhido do config.json
        proportions = self.config['day_profiles'][chosen_day_profile]

        # Distribui o volume da semana entre os dias com base nas proporções
        for day, proportion in proportions.items():
            day_volume = week_volume * proportion
            self.daily_volume[day].append(day_volume)


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
