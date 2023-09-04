import json
import random
import numpy as np
import csv
import os
from datetime import datetime, timedelta
from .tickets import Ticket 


class Simulation:
    def __init__(self, config):
        """
        Initialize a new Simulation object.

        :param config: Dictionary containing the simulation settings.
        """
        self.config = config
        self.default_config = config['default']
        self.tickets = []
        self.weekly_volume = []
        self.daily_volume = {}
        self.hourly_volume = {}
        self.start_date = None
        self.end_date = None
        

    def update_config(self, new_config):
        """
        Update the simulation settings.

        :param new_config: Dictionary containing new simulation settings.
        """
        # Atualizar as configurações com os novos valores fornecidos.
        self.default_config.update(new_config.get('default', {}))

    
    def distribute_volume_among_weeks(self):
        """
        Distributes the average monthly volume of tickets among the weeks of the month.
        """
        # Retrieve the operation size from the configuration
        operation_size = self.config['operation_sizes'][self.default_config['size_profile']]
        
        # Check if operation_size is a list and choose a random integer within the range
        if isinstance(operation_size, list):
            operation_size = random.randint(operation_size[0], operation_size[1])
        
        # Calculate the total number of days and weeks in the given time period
        total_days = (self.end_date - self.start_date).days
        full_weeks, extra_days = divmod(total_days, 7)
        
        # Allowed variation (in percentage) for distributing volume among weeks
        min_variation, max_variation = 23, 29  
        remaining_volume = operation_size
        self.weekly_volume = []

        # Distribute volume among full weeks
        for i in range(full_weeks):
            min_allowed = int(operation_size * min_variation / 100)
            max_allowed = int(operation_size * max_variation / 100)
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
            if day not in self.daily_volume:
                self.daily_volume[day] = []
            self.daily_volume[day].append(day_volume)


    def distribute_volume_intraday(self, day_volume):
        """
        Distributes the average daily volume of tickets among the hours of the day
        using a Gaussian distribution model.

        :param day_volume: Total volume of tickets for the day.
        """
        # Retrieve operation hours from the config
        operation_start = self.default_config['operation_hours']['start']
        operation_end = self.default_config['operation_hours']['end']
        # Retrieve the chosen intraday profile from the config
        intraday_profile = self.default_config['chosen_intraday_profile']
        profile_params = self.config['intraday_profiles'][intraday_profile]
        # Generate Gaussian curve
        hours = np.arange(operation_start, operation_end)
        amplitude = profile_params['gaussian_peaks'][0]['amplitude']
        center = profile_params['gaussian_peaks'][0]['center']
        width = profile_params['gaussian_peaks'][0]['width']
        curve = amplitude * np.exp(-0.5 * ((hours - center) / width)**2)
        # Add noise to the curve
        noise = np.random.normal(0, 0.05, curve.shape)
        curve += noise
        # Normalize the curve so that it sums to 1
        curve /= np.sum(curve)
        # Distribute the volume
        hourly_volume = curve * day_volume
        self.hourly_volume = {str(hour): vol for hour, vol in zip(hours, hourly_volume)}


    def generate_ticket(self):
        """
        Generates a random ticket based on the simulation settings and adds it to
        the tickets list.
        """
        # Generate a unique ID for the ticket (using the current size of the 'tickets' list)
        ticket_id = random.randint(1000000, 99999999)

        # Choose an hour of the day based on the hourly volume
        chosen_hour = random.choices(
            list(self.hourly_volume.keys()),
            weights=list(self.hourly_volume.values()),
            k=1
        )[0]

        # Generate random minute and second
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)

        # Generate a random date within the range between start_date and end_date,
        # but fix the hour to the chosen one
        random_date = self.start_date + (self.end_date - self.start_date) * random.random()
        start_time = random_date.replace(hour=int(chosen_hour), minute=random_minute, second=random_second)

        # Generate an end time for the ticket, which is a random value of 1 to 10 minutes after the start time.
        end_time = start_time + timedelta(minutes=random.randint(1, 10))

        # Randomly select a type for the ticket from a list of possible types.
        ticket_type = random.choice(["voice", "chat", "email"])

        # Create a new Ticket object with the generated values.
        new_ticket = Ticket(ticket_id, start_time, end_time, ticket_type)

        # Add the new Ticket object to the list of tickets.
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
        # Determine the total number of days in the simulation range.
        total_days = (self.end_date - self.start_date).days

        # First distribute the volume among weeks and days
        self.distribute_volume_among_weeks()
        
        # Run a loop to generate the total number of tickets.
        for week_volume in self.weekly_volume:
            self.distribute_volume_among_days(week_volume)
            for day, day_volumes in self.daily_volume.items():
                for day_volume in day_volumes:
                    self.distribute_volume_intraday(day_volume)
                    for _ in range(int(day_volume)):
                        self.generate_ticket()



    def export_to_csv(self, file_name_prefix='../data_out/tickets'):
        """
        Exports the generated tickets to a CSV file.
        
        :param file_name_prefix: The prefix of the CSV file to write to.
        """
        # Gerar um carimbo de data/hora para tornar o nome do arquivo único
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f'{file_name_prefix}_{timestamp}.csv'
        
        # Criar o diretório se ele não existir
        directory = os.path.dirname(file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_name, 'w', newline='') as csvfile:
            fieldnames = ['Ticket ID', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for ticket in self.tickets:
                writer.writerow({
                    'Ticket ID': ticket.ticket_id,
                    'Start Date': ticket.start_time.date(),
                    'Start Time': ticket.start_time.time().strftime('%H:%M:%S'),
                    'End Date': ticket.end_time.date(),
                    'End Time': ticket.end_time.time().strftime('%H:%M:%S'),
                    'Type': ticket.ticket_type
                })
