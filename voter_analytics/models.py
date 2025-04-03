# models.py
# this file defines the data models for the voter analytics app
# the 'Voter' model represents a voter, with fields for personal details,
# address, election participation, and voter score
# the 'load_data' function is responsible for loading voter data from a csv file into the database
# 'print_all_voters' prints out all voter records stored in the database.from django.db import models

class Voter(models.Model):
    # personal information of the voter
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    street_num = models.CharField(max_length=10)
    street_name = models.CharField(max_length=200)
    apt_num = models.CharField(max_length=20, null=True, blank=True)    # optional apartment number
    zip_code = models.CharField(max_length=10)
    dob = models.DateField()    # date of birth
    reg_date = models.DateField()   # when person registered to vote
    party = models.CharField(max_length=2)  # party affiliation
    precinct_num = models.CharField(max_length=5)

    # election participation flags (true or false)
    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)

    # voter score, an integer value
    voter_score = models.IntegerField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}, Party: {self.party}, Precinct: {self.precinct_num}, Score: {self.voter_score}'

def load_data():
    '''function to load data records from a csv file into django model instances.'''
    # delete all existing voter records to avoid duplicates when reloading
    Voter.objects.all().delete()
    # specify the path to the csv file
    filename = '/Users/elitsamincheva/Downloads/newton_voters.csv'
    f = open(filename)
    # skip the first line of the file (headers)
    f.readline() 

    # loop through each line in the csv file and create a new voter object
    for line in f:

        fields = line.split(',')
    
        # create a new Voter instance with the fields from the csv
        voter = Voter(first_name=fields[2],
                        last_name=fields[1],
                        street_num = fields[3],
                        street_name = fields[4],
                        apt_num = fields[5] if fields[5] else None,
                        zip_code = fields[6],
                        dob = fields[7],
                        reg_date = fields[8],
                        party = fields[9],
                        precinct_num = fields[10],
                        # convert to boolean for election participation
                        v20state = fields[11].upper() == "TRUE",
                        v21town = fields[12].upper() == "TRUE",
                        v21primary = fields[13].upper() == "TRUE",
                        v22general = fields[14].upper() == "TRUE",
                        v23town = fields[15].upper() == "TRUE",
                        voter_score = fields[16],
                )
        voter.save()    # save the voter to the database
        
        # print(f'Created result: {voter}')
        
def print_all_voters():
    for voter in Voter.objects.all():
        print(voter)
