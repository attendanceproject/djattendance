from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts.models import Trainee, User
from houses.models import House
from teams.models import Team
from terms.models import Term
from apimport.utils import save_locality


def new_trainee(trainees=[], gen="B", ct=1):
  for trainee in trainees:
    email = '.'.join(trainee[0].lower().split(' ')) + "@gmail.com"
    fname, lname = trainee[0].split(' ', 1)
    password = 'ap'
    dob = '1993-11-13'
    h = House.objects.get(name=trainee[1])
    t = Team.objects.get(name=trainee[2])
    l = save_locality(trainee[3], trainee[4], trainee[5])
    sa = ct > 2  # default value to be adjusted as necessary on a trainee by trainee basis :)
    u = Trainee(email=email, firstname=fname, lastname=lname, gender=gen, type='R', date_of_birth=dob, current_term=ct, is_active=True, team=t, house=h, locality=l, self_attendance=sa)
    u.set_password(password)
    u.save()


class Command(BaseCommand):
  # to use: python ap/manage.py populate_trainees --settings=ap.settings.dev
  def _create_trainees(self):
    # change the array below to get different trainees
    trainees = [("Yi Sun", "2121 Chalet", "Community - Orange", "Atlanta", "GA", "US"), ("Will Wang", "2464 Rainbow", "Children - Lake Forest", "Austin", "TX", "US"), ("Chris Bi", "905 Neptune", "University of California Irvine", "Beijing", "0", "CN"), ("Rick Petkau", "905 Neptune", "Orange Coast College", "Belmopan", "0", "BZ"), ("Samuel Swei", "2107 Grace Ct.", "Community - Irvine", "Berkeley", "CA", "US"), ("Daniel Tai", "2104 Grace Ct.", "Mount San Antonio College", "Berkeley", "CA", "US"), ("Julius Chang", "2360 Moro", "Community - Cerritos", "Boston", "MA", "US"), ("Samuel Kwong", "2103 Grace Ct.", "Cal Poly Pomona", "Charlottesville", "VA", "US"), ("Samuel Gutierrez", "2105 Grace Ct.", "University of California, Los Angeles", "Chula Vista", "CA", "US"), ("Brandon Alford", "2108 Grace Ct.", "Young People - Diamond Bar", "Conway", "AR", "US"), ("Rui Jiang", "2111 Grace Ct.", "Community - Diamond Bar", "Davis", "CA", "US"), ("Isaac Tsou", "2102 Grace Ct.", "Orange Coast College", "Davis", "CA", "US"), ("Carlos Marin", "2106 Grace Ct. Couple", "East LA College", "El Paso", "TX", "US"), ("Ryan Li", "1014 Modena", "Young People - Long Beach", "Hacienda Heights", "CA", "US"), ("Mark Fan", "2464 Rainbow", "Pasadena City College", "Houston", "TX", "US"), ("Nestor Zepeda", "2360 Moro", "Cal State University Fullerton", "Irvine", "CA", "US"), ("William Jeng", "905 Neptune", "Children - Santa Ana", "Irvine", "CA", "US"), ("Andres Mendoza", "2107 Grace Ct.", "Long Beach", "Irvine", "CA", "US"), ("Jonathan Robbins", "2111 Grace Ct.", "Community - Anaheim D5", "Irving", "TX", "US"), ("Stephen Kwan", "2104 Grace Ct.", "Young People - San Juan Capistrano", "Knoxville", "TN", "US"), ("Luke Cui", "2106 Grace Ct.", "Mount San Antonio College", "Los Angeles", "CA", "US"), ("Drew Kohnle", "2111 Grace Ct.", "Chapman College", "Lubbock", "TX", "US"), ("Garrett Macnee", "2121 Chalet", "Saddleback College", "Lubbock", "TX", "US"), ("Rafael Diaz", "2109 Grace Ct.", "Saddleback College", "Miami", "FL", "US"), ("Frank Martinez", "2104 Grace Ct.", "University of California Irvine", "Miami", "FL", "US"), ("Jacob Roberts", "2121 Chalet", "Cal State University Fullerton", "Milwaukee", "WI", "US"), ("David Lee", "1014 Modena", "Community - Anaheim D3", "New York City", "NY", "US"), ("Nkhosi Gama", "2108 Grace Ct.", "Santiago Canyon College", "Norman", "OK", "US"), ("Jasper Kuhn", "2104 Grace Ct.", "Cerritos College", "Plano", "TX", "US"), ("Samuel Yeh", "2105 Grace Ct.", "Community - Anaheim D1", "Plano", "TX", "US"), ("Dominic Tey", "2464 Rainbow", "Orange Coast College", "Plano", "TX", "US"), ("Josh Cherng", "2107 Grace Ct.", "Young People - Walnut", "Portland", "OR", "US"), ("Micah Sy Lato", "2109 Grace Ct.", "Pasadena City College", "Quezon City", "0", "PH"), ("Adam Sy", "2102 Grace Ct.", "University of Southern California", "Quezon City", "0", "PH"), ("Peter Ho", "2106 Grace Ct.", "Young People - Eastvale", "Reno", "NV", "US"), ("Christian Diaz", "2105 Grace Ct.", "Community - Cerritos", "Richmond", "0", "CA"), ("George Goodwin", "2360 Moro", "Cal Poly Pomona", "Riverside", "CA", "US"), ("Josue Pacheco", "2360 Moro", "Community - Anaheim D2", "Riverside", "CA", "US"), ("Jesse Avila", "2107 Grace Ct.", "Young People - Anaheim", "Riverside", "CA", "US"), ("Alex Cantu", "2105 Grace Ct. Couple", "Young People - Irvine", "San Antonio", "TX", "US"), ("Josh Carbunck", "2108 Grace Ct.", "Community - Orange", "Santa Barbara", "CA", "US"), ("Titus Ting", "2360 Moro", "Children - Anaheim", "Singapore", "0", "SG"), ("Henry C. Chen", "2107 Grace Ct.", "Young People - Anaheim", "St. Louis", "MO", "US"), ("Isaac Kuo", "2108 Grace Ct.", "Young People - Huntington Beach", "Torrance", "CA", "US"), ("Carson Maher", "2106 Grace Ct.", "Cypress College", "Tyler", "TX", "US"), ("Elijah Chang", "2103 Grace Ct.", "Young People - Anaheim", "Walnut", "CA", "US"), ("Jasper Han", "2102 Grace Ct.", "Young People - Anaheim", "Woodbridge", "CT", "US")]
    new_trainee(trainees, 'B', 1)

    trainees = [("Mark Allijohn", "2102 Grace Ct.", "Cypress College", "All Saints", "0", "AG"), ("Chris Jackson", "COMMUTER", "Young People - Irvine", "Athens", "GA", "US"), ("Austin Anderson", "2108 Grace Ct.", "California Institute of Technology", "Austin", "TX", "US"), ("Joseph Hernandez", "Hall Apt. 1-West", "Young People - Anaheim", "Austin", "TX", "US"), ("Connor Robinson", "2107 Grace Ct.", "Young People - Irvine", "Austin", "TX", "US"), ("Ben Findeisen", "2120 Grace Ct. Couple", "Young People - Santa Ana", "Austin", "TX", "US"), ("Joshua Tjokrosurjo", "2104 Grace Ct.", "Cerritos College", "Baltimore", "MD", "US"), ("Carlos Salamanca", "2105 Grace Ct.", "Long Beach", "College Station", "TX", "US"), ("Joe Yu", "COMMUTER", "Orange Coast College", "Cupertino", "CA", "US"), ("Sven Lee", "2104 Grace Ct.", "University of California Irvine", "Dallas", "TX", "US"), ("Tommy Lockwood", "2104 Grace Ct.", "Young People - Irvine", "Dallas", "TX", "US"), ("Clarence So", "2111 Grace Ct.", "Cypress College", "Hong Kong", "0", "CN"), ("Ryan Armstrong", "2109 Grace Ct.", "University of California, Los Angeles", "Houston", "TX", "US"), ("Daniel Jenkins", "COMMUTER", "University of California Irvine", "Irvine", "CA", "US"), ("David Ye", "2104 Grace Ct.", "East LA College", "Long Beach", "CA", "US"), ("Daniel Martin", "2111 Grace Ct.", "University of Southern California", "Long Beach", "CA", "US"), ("Kenny Nguyen", "2109 Grace Ct.", "Young People - Anaheim", "Los Angeles", "CA", "US"), ("Eric Song", "905 Neptune", "Cal State University Los Angeles", "Pleasanton", "CA", "US"), ("David Hanson", "2105 Grace Ct.", "Community - Anaheim D5", "Seattle", "WA", "US"), ("Brian Muller", "2106 Grace Ct.", "Young People - Santa Ana", "Seattle", "WA", "US"), ("Ebenezer Lee", "2103 Grace Ct.", "Cerritos College", "Singapore", "0", "SG"), ("Sean David", "2102 Grace Ct. Couple", "Young People - Anaheim", "Singapore", "0", "SG"), ("Ray Ding", "2111 Grace Ct.", "Community - Anaheim D4", "Toronto", "0", "CA"), ("Charles Pan", "905 Neptune", "Community - Diamond Bar", "Vancouver", "0", "CA"), ("Jacob Lin", "2116 Grace Ct. Couple", "Children - Diamond Bar", "Wichita", "KS", "US")]
    new_trainee(trainees, 'B', 2)

    trainees = [("Johnny Zhao", "905 Neptune", "Orange Coast College", "Alhambra", "CA", "US"), ("Shaun Pan", "1014 Modena", "Cal State University Los Angeles", "Anaheim", "CA", "US"), ("Basel Almachraki", "2102 Grace Ct.", "Community - Orange", "Anaheim", "CA", "US"), ("Ryan Holt", "2103 Grace Ct.", "Santa Ana College", "Arlington", "TX", "US"), ("Kyle Yen", "2360 Moro", "Children - Orange", "Austin", "TX", "US"), ("Austin Zhang", "2111 Grace Ct.", "Community - Anaheim D1", "Austin", "TX", "US"), ("Ty Wilson", "2108 Grace Ct.", "Young People - Santa Ana", "Austin", "TX", "US"), ("Luke Lu", "2107 Grace Ct.", "Young People - Cerritos", "Berkeley", "CA", "US"), ("Bill Yeh", "2109 Grace Ct.", "Young People - Fullerton", "Berkeley", "CA", "US"), ("Mauricio Gonzalez", "Hall Apt. 4-West", "Community - Anaheim D4", "Boca Raton", "FL", "US"), ("Nathan Bodrug", "Hall Apt. 2-West", "Children - Anaheim", "Calgary", "0", "CA"), ("Jack Ji", "2108 Grace Ct.", "California Institute of Technology", "Cambridge", "MA", "US"), ("Dennis Huang", "905 Neptune", "Young People - San Juan Capistrano", "Cambridge", "MA", "US"), ("Matthew Au", "2109 Grace Ct.", "Community - Anaheim D4", "Champaign", "IL", "US"), ("David Sun", "2106 Grace Ct.", "University of Southern California", "Charlottesville", "VA", "US"), ("Preston Wang", "2109 Grace Ct.", "University of Southern California", "Chicago", "IL", "US"), ("Johnny Stone", "2107 Grace Ct.", "Community - Fullerton", "College Station", "TX", "US"), ("George Ashebo", "905 Neptune", "Community - Anaheim D3", "Columbus", "OH", "US"), ("Drew Hawthorn", "2117 Grace Ct. Couple", "Community - Fullerton", "Conway", "AR", "US"), ("Jonathan Karr", "2111 Grace Ct.", "University of California Riverside", "Fort Collins", "CO", "US"), ("Jason Yeung", "2107 Grace Ct.", "Young People - Fullerton", "Franklin", "NJ", "US"), ("Jasper Duan", "2111 Grace Ct.", "Young People - Santa Ana", "Lawrence", "NJ", "US"), ("Henry Chen", "2102 Grace Ct.", "Young People - Diamond Bar", "Houston", "TX", "US"), ("Marvin Igwe", "2464 Rainbow", "Young People - Huntington Beach", "Houston", "TX", "US"), ("Christian Yu", "2360 Moro", "Young People - Irvine", "Houston", "TX", "US"), ("Peng Chen", "2102 Grace Ct.", "Cal Poly Pomona", "Irvine", "CA", "US"), ("Christopher Valencia", "2121 Chalet", "Cerritos College", "Irvine", "CA", "US"), ("Gregory Lee", "Hall Apt. 5-West", "Young People - Anaheim", "Irvine", "CA", "US"), ("Nazarite Goh", "2464 Rainbow", "East LA College", "Kota Samarahan", "0", "MY"), ("Matt Martin", "2105 Grace Ct.", "Young People - Long Beach", "Lancaster", "PA", "US"), ("Sam Cummings", "2109 Grace Ct.", "Chapman College", "Los Angeles", "CA", "US"), ("Miles Mistler", "2104 Grace Ct.", "Long Beach", "Los Angeles", "CA", "US"), ("Misael Trejo", "1014 Modena", "Children - Cypress", "Lubbock", "TX", "US"), ("Paul Wen", "2107 Grace Ct.", "Cal State University Fullerton", "Merced", "CA", "US"), ("Randy Juste", "2111 Grace Ct.", "Cerritos College", "Miami", "FL", "US"), ("Michael Cofino", "2103 Grace Ct.", "Children - Anaheim", "Miami", "FL", "US"), ("Johnathan Lin", "2108 Grace Ct.", "Orange Coast College", "Montreal", "0", "CA"), ("Jeff Yang", "2108 Grace Ct.", "Young People - Eastvale", "Newton", "MA", "US"), ("Abraham Goshay", "905 Neptune", "Cypress College", "Phoenix", "AZ", "US"), ("Daniel Wu", "2106 Grace Ct.", "University of California Riverside", "Phoenix", "AZ", "US"), ("Eric Pan", "2109 Grace Ct.", "Young People - Diamond Bar", "Piscataway", "NJ", "US"), ("Matthew Lee", "Hall Apt. 2-East", "Cal Poly Pomona", "Raleigh", "NC", "US"), ("Samuel Duan", "COMMUTER", "Mount San Antonio College", "Raleigh", "NC", "US"), ("Benjamin Liu", "2103 Grace Ct.", "University of California Riverside", "Richmond", "0", "CA"), ("Jeffrey Cheung", "2121 Chalet", "Santiago Canyon College", "Riverside", "CA", "US"), ("Enoch Huang", "2105 Grace Ct.", "Young People - Walnut", "Riverside", "CA", "US"), ("Edgardo Mendoza", "2104 Grace Ct.", "Cypress College", "Roseville", "CA", "US"), ("Justin Washington", "2106 Grace Ct.", "Saddleback College", "San Antonio", "TX", "US"), ("Andrew Jen", "2106 Grace Ct.", "East LA College", "San Diego", "CA", "US"), ("Jun Heo", "905 Neptune", "Young People - Cerritos", "San Diego", "CA", "US"), ("Kevin Sung", "2105 Grace Ct.", "Community - Anaheim D2", "San Jose", "CA", "US"), ("Kevin Yum", "2121 Chalet", "Young People - Irvine", "Santa Clara", "CA", "US"), ("David Welk", "2360 Moro", "Mount San Antonio College", "Seattle", "WA", "US"), ("Dhaval Kashyap", "2360 Moro", "Community - Anaheim D3", "Tallahassee", "FL", "US"), ("Jack Hu", "2104 Grace Ct.", "Cal State University Fullerton", "Toronto", "0", "CA"), ("Allen Liu", "2113 Grace Ct. Couple", "Community - Cerritos", "Toronto", "0", "CA"), ("Ed Galaska", "2121 Chalet", "Community - Diamond Bar", "Wickliffe", "OH", "US"), ("JayWynn Dueck", "1014 Modena", "University of California Irvine", "Winnipeg", "0", "CA")]
    new_trainee(trainees, 'B', 3)

    trainees = [("Julian Arango", "2106 Grace Ct.", "Community - Anaheim D2", "Atlanta", "GA", "US"), ("Daniel Teng", "905 Neptune", "Children - Santa Ana", "Champaign", "IL", "US"), ("Ian Wolf", "2360 Moro", "University of California, Los Angeles", "Chicago", "IL", "US"), ("Dustin Davis", "2121 Chalet", "Cypress College", "Conway", "AR", "US"), ("Joshua Obidah", "2111 Grace Ct.", "Fullerton College", "Cypress", "CA", "US"), ("Leo Medina", "2107 Grace Ct.", "Santa Ana College", "East Los Angeles", "CA", "US"), ("Rodney Rodriguez", "2103 Grace Ct.", "University of California Irvine", "East Los Angeles", "CA", "US"), ("Kevin Ger", "COMMUTER", "Community - Anaheim D1", "Fremont", "CA", "US"), ("Joon Jo", "2121 Grace Ct. Couple", "Community - Irvine", "Fullerton", "CA", "US"), ("David Tai", "2111 Grace Ct.", "University of California Irvine", "Huntington Beach", "CA", "US"), ("Joseph Duque", "2102 Grace Ct.", "Cal State University Fullerton", "Irvine", "CA", "US"), ("John Ferrante", "2102 Grace Ct.", "Children - Cypress", "Atlanta", "GA", "US"), ("Terry Hung", "2102 Grace Ct.", "Santa Ana College", "Kitchener", "0", "CA"), ("Jacob Chen", "2108 Grace Ct.", "Saddleback College", "Los Angeles", "CA", "US"), ("Jarrod Frankum", "905 Neptune", "University of California Irvine", "Lubbock", "TX", "US"), ("Paul Sutton", "2105 Grace Ct.", "University of California, Los Angeles", "Lubbock", "TX", "US"), ("Samuel Chiu", "1014 Modena", "Cerritos College", "Manila", "0", "PH"), ("Jonathan Tey", "2108 Grace Ct.", "Children - Anaheim", "Plano", "TX", "US"), ("Joseph Meng", "2109 Grace Ct.", "Community - Diamond Bar", "Portland", "OR", "US"), ("Philip Lam", "1014 Modena", "Fullerton College", "Portland", "OR", "US"), ("Peter Cheng", "2360 Moro", "Young People - Diamond Bar", "San Diego", "CA", "US"), ("Andreas Andreas", "2464 Rainbow", "Long Beach", "Vancouver", "0", "CA"), ("Jean Jeong", "2108 Grace Ct.", "Santa Ana College", "Vancouver", "0", "CA"), ("Michael Ng", "2107 Grace Ct.", "Cal State University Fullerton", "Washington DC", "DC", "US"), ("Ben Wang", "2104 Grace Ct.", "University of California Riverside", "Washington DC", "DC", "US")]
    new_trainee(trainees, 'B', 4)

    trainees = [("Sabrina Borunda", "2380 Hansen", "Young People - Fullerton", "Albuquerque", "NM", "US"), ("Hannah Lee", "2117 Grace Ct.", "Long Beach", "Anaheim", "CA", "US"), ("Dana Martin", "2360 Hansen", "Orange Coast College", "Anaheim", "CA", "US"), ("Phoebe Lee", "2345 Caramia", "Young People - Huntington Beach", "Anaheim", "CA", "US"), ("Kelli Mann", "2112 Grace Ct.", "Community - Anaheim D5", "Austin", "TX", "US"), ("Chili Lee", "2371 Caramia", "Community - Irvine", "Austin", "TX", "US"), ("Daniela Cheung", "2114 Grace Ct.", "University of California Irvine", "Austin", "TX", "US"), ("Elizabeth Gonzales", "2113 Grace Ct.", "Young People - Anaheim", "Austin", "TX", "US"), ("Taylor Cole", "2371 Caramia", "Young People - Anaheim", "Austin", "TX", "US"), ("Sebrina Yan", "2115 Grace Ct.", "Young People - Santa Ana", "Austin", "TX", "US"), ("Boeun Lee", "2112 Grace Ct.", "Young People - Anaheim", "Bellevue", "WA", "US"), ("Hannah Penner", "2115 Grace Ct.", "Children - San Juan Capistrano", "Belmopan", "0", "BZ"), ("Tae Suh", "2120 Grace Ct.", "Cal State University Los Angeles", "Boston", "MA", "US"), ("Tiffany Chua", "2116 Grace Ct.", "Community - Anaheim D4", "Champaign", "IL", "US"), ("Serena Lee", "2345 Caramia", "Community - Orange", "Champaign", "IL", "US"), ("Xuefei Zheng", "2371 Caramia", "Young People - Anaheim", "Champaign", "IL", "US"), ("Amarachi Ibe", "2115 Grace Ct.", "Young People - Irvine", "Champaign", "IL", "US"), ("Adilenne Garcia", "1041 Reiser", "Children - Santa Ana", "Chula Vista", "CA", "US"), ("Kaylin Wiseman", "1060 Stephenson", "Community - Anaheim D2", "Cincinnati", "OH", "US"), ("Joanna Tan", "1014 Gilbert", "Children - Fullerton", "Columbus", "OH", "US"), ("Claire Huang", "2380 Hansen", "Mount San Antonio College", "Coquitlam", "0", "CA"), ("Regina Suwuh", "2119 Grace Ct.", "Community - Anaheim D1", "Dallas", "TX", "US"), ("Flor Manzanares", "1014 Gilbert", "Cypress College", "Dallas", "TX", "US"), ("Brenda Penner", "2118 Grace Ct.", "Community - Irvine", "Davis", "CA", "US"), ("Elizabeth Chan", "2121 Grace Ct.", "Santiago Canyon College", "Davis", "CA", "US"), ("Sierra Shepard", "2118 Grace Ct.", "Community - Anaheim D4", "Denton", "TX", "US"), ("Amy Yung", "1041 Reiser", "Young People - Santa Ana", "Denver", "CO", "US"), ("Sheryl Pu", "2117 Grace Ct.", "University of Southern California", "Diamond Bar", "CA", "US"), ("Keila Rios", "2121 Grace Ct.", "Fullerton College", "Edinburg", "TX", "US"), ("Liliana Marin", "2106 Grace Ct. Couple", "East LA College", "El Paso", "TX", "US"), ("Kenya Neal", "2116 Grace Ct.", "University of California Irvine", "Gainesville", "FL", "US"), ("Janine Xiang", "2121 Grace Ct.", "Children - Anaheim", "Glasgow", "0", "GB"), ("Elisa Melo", "2121 Grace Ct.", "Children - Orange", "Goiania", "0", "BZ"), ("Ruth Long", "1041 Reiser", "Community - Fullerton", "Houston", "TX", "US"), ("Ana Carolina Corey", "2380 Hansen", "Young People - Anaheim", "Indianapolis", "IN", "US"), ("Angela Oliva", "1014 Gilbert", "Children - Fullerton", "Irvine", "CA", "US"), ("Kristie Ahn", "1015 Stephenson", "Children - San Juan Capistrano", "Irvine", "CA", "US"), ("Silvia Coto", "2117 Grace Ct.", "Community - Anaheim D3", "Irvine", "CA", "US"), ("Julia Chung", "2117 Grace Ct.", "Young People - Long Beach", "Irvine", "CA", "US"), ("Amanda Vetter", "2112 Grace Ct.", "Chapman College", "Kalamazoo", "MI", "US"), ("Amber Petrillo", "2119 Grace Ct.", "University of Southern California", "Kansas City", "KS", "US"), ("Shula Yuan", "2119 Grace Ct.", "Children - Anaheim", "Los Angeles", "CA", "US"), ("Anna Bachand", "2120 Grace Ct.", "Community - Anaheim D1", "Los Angeles", "CA", "US"), ("Susan Cheng", "2116 Grace Ct.", "Orange Coast College", "Los Angeles", "CA", "US"), ("Joy Herman", "2114 Grace Ct.", "Young People - Diamond Bar", "Los Angeles", "CA", "US"), ("Rina Liu", "2118 Grace Ct.", "Young People - Walnut", "Macau", "0", "CN"), ("Zhen Wang", "2114 Grace Ct.", "University of California Irvine", "Middleborough", "MA", "US"), ("Priscilla Wong", "2114 Grace Ct.", "Fullerton College", "Monterey Park", "CA", "US"), ("Amber Sun", "2116 Grace Ct.", "East LA College", "New York City", "NY", "US"), ("Allison Lin", "2112 Grace Ct.", "Long Beach", "New York City", "NY", "US"), ("JZ Hung", "1060 Stephenson", "Young People - Eastvale", "New York City", "NY", "US"), ("Connie Chen", "1045 Stephenson", "Children - Lake Forest", "Philadelphia", "PA", "US"), ("Charimar Valentin", "1015 Stephenson", "Cypress College", "Philadelphia", "PA", "US"), ("Jenny Liang", "2345 Caramia", "Young People - Irvine", "Philadelphia", "PA", "US"), ("Yuan Le", "2120 Grace Ct.", "Community - Anaheim D4", "Plano", "TX", "US"), ("Victoria Hung", "2113 Grace Ct.", "Young People - Irvine", "Plano", "TX", "US"), ("Christa Jeschke", "2113 Grace Ct.", "University of California Irvine", "Portland", "OR", "US"), ("Clara Lee", "2119 Grace Ct.", "Cal Poly Pomona", "Raleigh", "NC", "US"), ("Bridget Dou", "2112 Grace Ct.", "California Institute of Technology", "Raleigh", "NC", "US"), ("Kimberly Seria", "2114 Grace Ct.", "Cerritos College", "Regina", "0", "CA"), ("Deborah Chen", "2117 Grace Ct.", "Orange Coast College", "Richmond", "0", "CA"), ("Tammi Hua", "2119 Grace Ct.", "Pasadena City College", "Richmond", "0", "CA"), ("Jessica Chen", "2121 Grace Ct.", "Young People - Cerritos", "Richmond", "0", "CA"), ("Crystal Goh", "2360 Hansen", "Saddleback College", "Riverside", "CA", "US"), ("Eunice Tay", "1009 Cambria", "Young People - Fullerton", "Riverside", "CA", "US"), ("Amy Cantu", "2105 Grace Ct. Couple", "Young People - Irvine", "San Antonio", "TX", "US"), ("Grace Liang", "2360 Hansen", "Community - Diamond Bar", "San Bernardino", "CA", "US"), ("Isabel Mora", "1060 Stephenson", "Children - Irvine", "San Francisco", "CA", "US"), ("Tobi Abosede", "1045 Stephenson", "Community - Fullerton", "San Francisco", "CA", "US"), ("Rebecca Huang", "1009 Cambria", "Orange Coast College", "San Gabriel", "CA", "US"), ("April Park", "2360 Hansen", "Children - Irvine", "Seattle", "WA", "US"), ("Joanna Pan", "2113 Grace Ct.", "Children - Anaheim", "Shanghai", "0", "CN"), ("Ruth Lee", "1045 Stephenson", "Children - Cypress", "Singapore", "0", "SG"), ("Crystal Cabral", "2345 Caramia", "Santa Ana College", "South Gate", "CA", "US"), ("Natasha Schoenecker", "2115 Grace Ct.", "Children - Orange", "Spokane", "WA", "US"), ("Marian Sawada", "1045 Stephenson", "University of California, Los Angeles", "St. Catharines", "0", "CA"), ("Tanya Bae", "1041 Reiser", "Community - Anaheim D5", "Sydney", "0", "AU"), ("Sophia Xu", "2116 Grace Ct.", "Cal State University Fullerton", "Toronto", "0", "CA"), ("Joanna Rumbley", "1015 Stephenson", "Children - Anaheim", "Wickliffe", "OH", "US"), ("Serina X. Lee", "COMMUTER", "Community - Anaheim D2", "Wickliffe", "OH", "US"), ("Sarah Lin", "1014 Gilbert", "Young People - Fullerton", "Wickliffe", "OH", "US"), ("Vera Zhao", "2118 Grace Ct.", "University of California Irvine", "Xiamen", "0", "CN")]
    new_trainee(trainees, 'S', 1)

    trainees = [("Rachael Hernandez", "Hall Apt. 1-West", "Young People - Anaheim", "Austin", "TX", "US"), ("Rachel Chavana", "2121 Grace Ct.", "Young People - Huntington Beach", "Austin", "TX", "US"), ("Johanna Findeisen", "2120 Grace Ct. Couple", "Young People - Santa Ana", "Austin", "TX", "US"), ("Gabrielle Pryor", "2119 Grace Ct.", "Children - Santa Ana", "Bauru", "0", "BZ"), ("Emily Hu", "2345 Caramia", "Children - Diamond Bar", "Beijing", "0", "CN"), ("Jenn Phu", "2360 Hansen", "University of California Riverside", "Dallas", "TX", "US"), ("Cindy Mariano", "2116 Grace Ct.", "Santa Ana College", "Denton", "TX", "US"), ("Joanna Wiguna", "1015 Stephenson", "Cerritos College", "Diamond Bar", "CA", "US"), ("Priscilla Wang", "1014 Gilbert", "Cal Poly Pomona", "Houston", "TX", "US"), ("Nuria Dubon", "2112 Grace Ct.", "Santiago Canyon College", "Huntington Beach", "CA", "US"), ("Megan Ku", "1009 Cambria", "Orange Coast College", "Montreal", "0", "CA"), ("Annie Liang", "2371 Caramia", "Children - Anaheim", "New York City", "NY", "US"), ("Zoe Zhang", "2115 Grace Ct.", "Children - Anaheim", "Palo Alto", "CA", "US"), ("Yang Cheng", "2118 Grace Ct.", "Young People - Cerritos", "Pasadena", "CA", "US"), ("Rebecca Y. Chen", "1015 Stephenson", "Children - Lake Forest", "San Jose", "CA", "US"), ("Shirleen Fang", "2120 Grace Ct.", "Young People - Cerritos", "Shenzhen", "0", "CN"), ("Janis Freeman", "2380 Hansen", "Community - Diamond Bar", "Shoreline", "WA", "US"), ("Elim Oh", "2117 Grace Ct.", "Cypress College", "Singapore", "0", "SG"), ("Lydia Lim", "1014 Gilbert", "Fullerton College", "Singapore", "0", "SG"), ("Anastasia David", "2102 Grace Ct. Couple", "Young People - Anaheim", "Singapore", "0", "SG"), ("Sandy Wang", "2113 Grace Ct.", "Cal State University Fullerton", "Sydney", "0", "AU"), ("Jura Lin", "2116 Grace Ct. Couple", "Children - Diamond Bar", "Wichita", "KS", "US")]
    new_trainee(trainees, 'S', 2)

    trainees = [("Abib Cao", "2112 Grace Ct.", "Cal Poly Pomona", "Alhambra", "CA", "US"), ("Christie Pagan", "COMMUTER", "Community - Anaheim D2", "Anaheim", "CA", "US"), ("Abby Miner", "2117 Grace Ct.", "University of Southern California", "Athens", "GA", "US"), ("Kaitlin Hairston", "2118 Grace Ct.", "Children - San Juan Capistrano", "Austin", "TX", "US"), ("Sarah Chen", "2113 Grace Ct.", "Community - Anaheim D3", "Austin", "TX", "US"), ("Karina Lozada", "1045 Stephenson", "Long Beach", "Austin", "TX", "US"), ("Jacqueline Elizondo", "2119 Grace Ct.", "University of California, Los Angeles", "Austin", "TX", "US"), ("Camille Bianan", "2117 Grace Ct.", "Young People - Eastvale", "Austin", "TX", "US"), ("Rachel Ard", "2345 Caramia", "Young People - Irvine", "Austin", "TX", "US"), ("Stacy Castillo", "1009 Cambria", "Young People - Long Beach", "Austin", "TX", "US"), ("Indigo Lu", "2112 Grace Ct.", "Community - Anaheim D1", "Baton Rouge", "LA", "US"), ("Sophia He", "2380 Hansen", "Community - Anaheim D2", "Beijing", "0", "CN"), ("Stephanie Wang", "1060 Stephenson", "Young People - San Juan Capistrano", "Berkeley", "CA", "US"), ("Hannah Oh", "1041 Reiser", "Young People - Walnut", "Berkeley", "CA", "US"), ("Lorena Roca", "COMMUTER", "Children - Cypress", "Boca Raton", "FL", "US"), ("Priscila Gonzalez", "Hall Apt. 4-West", "Community - Anaheim D4", "Boca Raton", "FL", "US"), ("Lisa Matamoros", "COMMUTER", "Cypress College", "Boston", "MA", "US"), ("Hilary Bodrug", "Hall Apt. 2-West", "Children - Anaheim", "Calgary", "0", "CA"), ("Katya Becker", "1045 Stephenson", "Long Beach", "Cambridge", "MA", "US"), ("Eve Wang", "2113 Grace Ct.", "University of California Irvine", "Cambridge", "MA", "US"), ("Tina Chang", "1045 Stephenson", "Cal State University Los Angeles", "Cerritos", "CA", "US"), ("Lisa Welk", "2120 Grace Ct.", "University of California Irvine", "Cheney", "WA", "US"), ("Michelle Liu", "2114 Grace Ct.", "Pasadena City College", "Chicago", "IL", "US"), ("Ruth Liang", "2114 Grace Ct.", "University of California Irvine", "Columbus", "OH", "US"), ("Hannah Hawthorn", "2117 Grace Ct. Couple", "Community - Fullerton", "Conway", "AR", "US"), ("Kayla Guilliams", "2115 Grace Ct.", "Orange Coast College", "Conway", "AR", "US"), ("Emily Liu", "1041 Reiser", "Saddleback College", "Cupertino", "CA", "US"), ("Caric Chow", "1041 Reiser", "Cal Poly Pomona", "Davis", "CA", "US"), ("Joana Morales", "1009 Cambria", "University of Southern California", "Davis", "CA", "US"), ("Athena Clark", "2117 Grace Ct.", "Children - Anaheim", "Denton", "TX", "US"), ("Stephanie Azubuike", "2120 Grace Ct.", "Young People - Anaheim", "Denton", "TX", "US"), ("Anna Johnsen", "2118 Grace Ct.", "Chapman College", "Denver", "CO", "US"), ("Chelsea Corpuz", "2116 Grace Ct.", "Children - Diamond Bar", "Dubai", "0", "AE"), ("Mayra Santiago", "2121 Grace Ct.", "Fullerton College", "Edinburg", "TX", "US"), ("Aaliyah Shen", "2371 Caramia", "Community - Diamond Bar", "Edinburgh", "0", "GB"), ("Danielle Jones", "2360 Hansen", "Young People - Diamond Bar", "Fairborn", "OH", "US"), ("Carrie Chambers", "2371 Caramia", "Cal Poly Pomona", "Fort Collins", "CO", "US"), ("Carmen Delgado", "2114 Grace Ct.", "Community - Anaheim D2", "Gainesville", "FL", "US"), ("Grace Cheng", "1041 Reiser", "Young People - Irvine", "Honolulu", "HI", "US"), ("Susanna Bruso", "1045 Stephenson", "Young People - Fullerton", "Houston", "TX", "US"), ("Jinhee Han", "2118 Grace Ct.", "Community - Diamond Bar", "Indianapolis", "IN", "US"), ("Shannon Wong", "2345 Caramia", "Children - Anaheim", "Irvine", "CA", "US"), ("Ann Huang", "2116 Grace Ct.", "Community - Fullerton", "Irvine", "CA", "US"), ("Jackie Arevalo", "1015 Stephenson", "Santiago Canyon College", "Irvine", "CA", "US"), ("Elizabeth Lee", "Hall Apt. 5-West", "Young People - Anaheim", "Irvine", "CA", "US"), ("Natalie Lau", "2120 Grace Ct.", "Young People - Walnut", "London", "0", "GB"), ("Joo Hee Eom", "1015 Stephenson", "Community - Orange", "Los Angeles", "CA", "US"), ("Jessica Yoon", "2345 Caramia", "Long Beach", "Los Angeles", "CA", "US"), ("Alice Qin", "1045 Stephenson", "Young People - Diamond Bar", "Los Angeles", "CA", "US"), ("Amanda Sulistyo", "1060 Stephenson", "Young People - Irvine", "Los Angeles", "CA", "US"), ("Shea Braddock", "2115 Grace Ct.", "Young People - Eastvale", "Lubbock", "TX", "US"), ("Amber Jamerson", "1060 Stephenson", "Young People - Huntington Beach", "Lubbock", "TX", "US"), ("Michelle Nevarez", "1014 Gilbert", "Children - Orange", "New York City", "NY", "US"), ("Stephanie Chukwuma", "1060 Stephenson", "Community - Anaheim D5", "New York City", "NY", "US"), ("Elaine Hoang", "2115 Grace Ct.", "Young People - Anaheim", "New York City", "NY", "US"), ("Anna Olson", "1014 Gilbert", "Young People - Huntington Beach", "Newton", "MA", "US"), ("Paige Wheaton", "2360 Hansen", "Community - Anaheim D2", "Norman", "OK", "US"), ("Mary Amelia Fichter", "1015 Stephenson", "Community - Irvine", "Omaha", "NE", "US"), ("Ruth Nan", "1014 Gilbert", "East LA College", "Omaha", "NE", "US"), ("Tiffaney Tatro", "1014 Gilbert", "Young People - Eastvale", "Omaha", "NE", "US"), ("Angela Wang", "2119 Grace Ct.", "Young People - Long Beach", "Pittsburgh", "PA", "US"), ("Mercy Chi", "1014 Gilbert", "Community - Cerritos", "Plano", "TX", "US"), ("Claire Lee", "Hall Apt. 2-East", "Cal Poly Pomona", "Raleigh", "NC", "US"), ("Grace Jou", "1060 Stephenson", "Children - Irvine", "Raleigh", "NC", "US"), ("Raven Lester", "1009 Cambria", "Cal State University Fullerton", "Reno", "NV", "US"), ("Selcy Borromeo", "2116 Grace Ct.", "Mount San Antonio College", "San Antonio", "TX", "US"), ("Raquel Morales", "2380 Hansen", "Mount San Antonio College", "San Francisco", "CA", "US"), ("Alice Wu", "1041 Reiser", "Young People - Anaheim", "San Francisco", "CA", "US"), ("Mary Strange", "2120 Grace Ct.", "Children - Fullerton", "San Jose", "CA", "US"), ("Vorah Shin", "2118 Grace Ct.", "Young People - Anaheim", "Sao Paulo", "0", "BZ"), ("Rebecca Chao", "2380 Hansen", "Cal State University Fullerton", "Seattle", "WA", "US"), ("Lydia Wong", "2345 Caramia", "Chapman College", "Singapore", "0", "SG"), ("Olivia Broussard", "2112 Grace Ct.", "University of California, Los Angeles", "Stillwater", "OK", "US"), ("Gladicel Flores", "2360 Hansen", "Santa Ana College", "Storrs", "CT", "US"), ("Tiffany Liu", "2113 Grace Ct. Couple", "Community - Cerritos", "Toronto", "0", "CA"), ("Sophie Chen", "2380 Hansen", "University of California Riverside", "Vancouver", "0", "CA"), ("Joyce Low", "2371 Caramia", "Young People - Irvine", "Vancouver", "0", "CA"), ("Laura Wilde", "1041 Reiser", "Cerritos College", "Waco", "TX", "US"), ("Elim Feng", "1014 Gilbert", "Community - Anaheim D3", "Wickliffe", "OH", "US")]
    new_trainee(trainees, 'S', 3)

    trainees = [("Yi Yuan", "2115 Grace Ct.", "East LA College", "Arcadia", "CA", "US"), ("Angel Vattakunnel", "2114 Grace Ct.", "Mount San Antonio College", "Austin", "TX", "US"), ("Sara Petkau", "1060 Stephenson", "University of California, Los Angeles", "Belmopan", "0", "BZ"), ("Benedicta Lee", "2360 Hansen", "Community - Diamond Bar", "Bloomfield", "MI", "US"), ("Sarah Yu", "2119 Grace Ct.", "Community - Anaheim D2", "Champaign", "IL", "US"), ("Rachel Woo", "2119 Grace Ct.", "Young People - Cerritos", "Champaign", "IL", "US"), ("Sarah Olson", "1015 Stephenson", "Community - Anaheim D5", "Charlotte", "NC", "US"), ("Sarah Li", "1041 Reiser", "Community - Cerritos", "College Station", "TX", "US"), ("Hannah Smith", "2121 Grace Ct.", "Children - Lake Forest", "Dunn Loring", "VA", "US"), ("Rossy Ramos", "2121 Grace Ct.", "Saddleback College", "Fort Worth", "TX", "US"), ("Melody Yang", "2371 Caramia", "Young People - Santa Ana", "Fremont", "CA", "US"), ("Nayeon Jo", "2121 Grace Ct. Couple", "Community - Irvine", "Fullerton", "CA", "US"), ("Lisa Lin", "2360 Hansen", "Children - Anaheim", "Fuzhou", "0", "CN"), ("Renewing Xu", "2345 Caramia", "Community - Anaheim D1", "Guangzhou", "0", "CN"), ("Erika Yang", "2115 Grace Ct.", "Chapman College", "Iowa City", "IA", "US"), ("Grace Sun", "2371 Caramia", "Cerritos College", "Los Angeles", "CA", "US"), ("Meng Ge", "2371 Caramia", "Santa Ana College", "Milford", "IA", "US"), ("Esther Tsai", "2360 Hansen", "Young People - Diamond Bar", "Nutley", "NJ", "US"), ("Viviana Figueroa", "2113 Grace Ct.", "California Institute of Technology", "Orange", "CA", "US"), ("Conomy Wang", "2345 Caramia", "Long Beach", "Riverside", "CA", "US"), ("Peace Lu", "1060 Stephenson", "Saddleback College", "Riverside", "CA", "US"), ("Tam Le", "2120 Grace Ct.", "Santiago Canyon College", "San Francisco", "CA", "US"), ("Ellie Hsu", "2114 Grace Ct.", "Young People - Walnut", "Toronto", "0", "CA"), ("Ya-Chien Chan", "2112 Grace Ct.", "Young People - San Juan Capistrano", "Woodbridge", "CT", "US")]
    new_trainee(trainees, 'S', 4)

    groups = []
    ams = ["Alford, Brandon", "Chen, Jessica", "Jou, Grace", "Juste, Randy", "Kohnle, Drew", "Ku, Megan", "Lee, Sven", "Liu, Michelle", "Stone, Johnny", "Vetter, Amanda"]
    groups.append(ams)
    groups.append('attendance_monitors')

    maintenance = ["Lester, Raven", "Lim, Lydia", "Allijohn, Mark", "Pan, Shaun", "Santiago, Mayra", "Trejo, Misael", "Galaska, Ed", "Bodrug, Nathan"]
    groups.append(maintenance)
    groups.append('maintenance')

    av = ["Huang, Enoch", "Lin, Jacob", "Yen, Kyle", "Chang, Julius", "Maher, Carson", "Ding, Ray"]
    groups.append(av)
    groups.append('av')

    service_schedulers = ["Huang, Dennis", "Ye, David"]
    groups.append(service_schedulers)
    groups.append('service_schedulers')

    badges = ["Yeh, Bill", "Oliva, Angela", "Zhang, Austin", "Wang, Angela", "Hoang, Elaine"]
    groups.append(badges)
    groups.append('badges')

    HC = ["Pan, Shaun", "Huang, Enoch", "Chen, Peng", "Wang, Preston", "Liu, Benjamin", "Yang, Jeff", "Mistler, Miles", "Hu, Jack", "Martin, Matt", "Sung, Kevin", "Washington, Justin", "Wu, Daniel", "Stone, Johnny", "Robinson, Connor", "Wilson, Ty", "Lin, Johnathan", "Cummings, Sam", "Pan, Eric", "Karr, Jonathan", "Juste, Randy", "Yum, Kevin", "Cheung, Jeffrey", "Yen, Kyle", "Yu, Christian", "Goh, Nazarite", "Igwe, Marvin", "Huang, Dennis", "Ashebo, George"]
    groups.append(HC)
    groups.append('HC')

    while(len(groups) > 0):
      g, created = Group.objects.get_or_create(name=groups.pop())
      for trainee in groups.pop():
        lname, fname = trainee.split(', ', 1)
        g.user_set.add(User.objects.get(firstname=fname, lastname=lname))

    trainees_to_tas = [
        ('Aaliyah Shen', 'Hannah'),
        ('Abby Miner', 'Hannah'),
        ('Abib Cao', 'Veronica'),
        ('Abraham Goshay', 'Joseph'),
        ('Adam Sy', 'Oscar'),
        ('Adilenne Garcia', 'Nikki'),
        ('Alex Cantu', 'Joe'),
        ('Alice Qin', 'Annie'),
        ('Alice Wu', 'Nikki'),
        ('Allen Liu', 'Paul'),
        ('Allison Lin', 'Veronica'),
        ('Amanda Sulistyo', 'Nikki'),
        ('Amanda Vetter', 'Veronica'),
        ('Amarachi Ibe', 'Veronica'),
        ('Amber Jamerson', 'Nikki'),
        ('Amber Petrillo', 'Raizel'),
        ('Amber Sun', 'Veronica'),
        ('Amy Cantu', 'Raizel'),
        ('Amy Yung', 'Nikki'),
        ('Ana Carolina Corey', 'Nikki'),
        ('Anastasia David', 'Annie'),
        ('Andres Mendoza', 'Oscar'),
        ('Andrew Jen', 'Jerome'),
        ('Angela Oliva', 'Annie'),
        ('Angela Wang', 'Raizel'),
        ('Ann Huang', 'Veronica'),
        ('Anna Bachand', 'Raizel'),
        ('Anna Johnsen', 'Raizel'),
        ('Anna Olson', 'Annie'),
        ('Annie Liang', 'Hannah'),
        ('April Park', 'Hannah'),
        ('Athena Clark', 'Hannah'),
        ('Austin Anderson', 'Joe'),
        ('Austin Zhang', 'Jerome'),
        ('Basel Almachraki', 'Walt'),
        ('Ben Findeisen', 'Walt'),
        ('Benjamin Liu', 'Oscar'),
        ('Bill Yeh', 'Oscar'),
        ('Boeun Lee', 'Veronica'),
        ('Brandon Alford', 'Jerome'),
        ('Brenda Penner', 'Raizel'),
        ('Brian Muller', 'Joe'),
        ('Bridget Dou', 'Veronica'),
        ('Camille Bianan', 'Hannah'),
        ('Caric Chow', 'Nikki'),
        ('Carlos Marin', 'Walt'),
        ('Carlos Salamanca', 'Walt'),
        ('Carmen Delgado', 'Hannah'),
        ('Carrie Chambers', 'Hannah'),
        ('Carson Maher', 'Joseph'),
        ('Charimar Valentin', 'Annie'),
        ('Charles Pan', 'Andrew'),
        ('Chelsea Corpuz', 'Veronica'),
        ('Chili Lee', 'Hannah'),
        ('Chris Bi', 'Paul'),
        ('Chris Jackson', 'Joe'),
        ('Christa Jeschke', 'Veronica'),
        ('Christian Diaz', 'Joe'),
        ('Christian Yu', 'Joseph'),
        ('Christie Pagan', 'Hannah'),
        ('Christopher Valencia', 'Jerome'),
        ('Cindy Mariano', 'Veronica'),
        ('Claire Huang', 'Nikki'),
        ('Claire Lee', 'Annie'),
        ('Clara Lee', 'Raizel'),
        ('Clarence So', 'Andrew'),
        ('Connie Chen', 'Annie'),
        ('Connor Robinson', 'Walt'),
        ('Crystal Cabral', 'Nikki'),
        ('Crystal Goh', 'Hannah'),
        ('Dana Martin', 'Hannah'),
        ('Daniel Jenkins', 'Joe'),
        ('Daniel Martin', 'Joe'),
        ('Daniel Tai', 'Andrew'),
        ('Daniel Wu', 'Andrew'),
        ('Daniela Cheung', 'Hannah'),
        ('Danielle Jones', 'Hannah'),
        ('David Hanson', 'Paul'),
        ('David Lee', 'Joseph'),
        ('David Sun', 'Oscar'),
        ('David Welk', 'Paul'),
        ('David Ye', 'Joe'),
        ('Deborah Chen', 'Hannah'),
        ('Dennis Huang', 'Andrew'),
        ('Dhaval Kashyap', 'Paul'),
        ('Dominic Tey', 'Oscar'),
        ('Drew Hawthorn', 'Walt'),
        ('Drew Kohnle', 'Walt'),
        ('Ebenezer Lee', 'Jerome'),
        ('Ed Galaska', 'Joe'),
        ('Edgardo Mendoza', 'Oscar'),
        ('Elaine Hoang', 'Veronica'),
        ('Elijah Chang', 'Joseph'),
        ('Elim Feng', 'Annie'),
        ('Elim Oh', 'Hannah'),
        ('Elisa Melo', 'Raizel'),
        ('Elizabeth Chan', 'Raizel'),
        ('Elizabeth Gonzales', 'Veronica'),
        ('Elizabeth Lee', 'Annie'),
        ('Emily Hu', 'Nikki'),
        ('Emily Liu', 'Nikki'),
        ('Enoch Huang', 'Joseph'),
        ('Eric Pan', 'Jerome'),
        ('Eric Song', 'Andrew'),
        ('Eunice Tay', 'Veronica'),
        ('Eve Wang', 'Veronica'),
        ('Flor Manzanares', 'Annie'),
        ('Frank Martinez', 'Walt'),
        ('Gabrielle Pryor', 'Raizel'),
        ('Garrett Macnee', 'Oscar'),
        ('George Ashebo', 'Paul'),
        ('George Goodwin', 'Walt'),
        ('Gladicel Flores', 'Hannah'),
        ('Grace Cheng', 'Nikki'),
        ('Grace Jou', 'Nikki'),
        ('Grace Liang', 'Hannah'),
        ('Gregory Lee', 'Walt'),
        ('Hannah Hawthorn', 'Annie'),
        ('Hannah Lee', 'Hannah'),
        ('Hannah Oh', 'Nikki'),
        ('Hannah Penner', 'Veronica'),
        ('Henry C. Chen', 'Jerome'),
        ('Henry Chen', 'Jerome'),
        ('Hilary Bodrug', 'Annie'),
        ('Indigo Lu', 'Veronica'),
        ('Isaac Kuo', 'Oscar'),
        ('Isaac Tsou', 'Andrew'),
        ('Isabel Mora', 'Nikki'),
        ('Jack Hu', 'Jerome'),
        ('Jack Ji', 'Andrew'),
        ('Jackie Arevalo', 'Annie'),
        ('Jacob Lin', 'Paul'),
        ('Jacob Roberts', 'Walt'),
        ('Jacqueline Elizondo', 'Raizel'),
        ('Janine Xiang', 'Raizel'),
        ('Janis Freeman', 'Nikki'),
        ('Jason Yeung', 'Jerome'),
        ('Jasper Duan', 'Andrew'),
        ('Jasper Han', 'Walt'),
        ('Jasper Kuhn', 'Walt'),
        ('JayWynn Dueck', 'Walt'),
        ('Jeff Yang', 'Jerome'),
        ('Jeffrey Cheung', 'Joe'),
        ('Jenn Phu', 'Hannah'),
        ('Jenny Liang', 'Nikki'),
        ('Jesse Avila', 'Andrew'),
        ('Jessica Chen', 'Raizel'),
        ('Jessica Yoon', 'Nikki'),
        ('Jinhee Han', 'Raizel'),
        ('Joana Morales', 'Veronica'),
        ('Joanna Pan', 'Veronica'),
        ('Joanna Rumbley', 'Annie'),
        ('Joanna Tan', 'Annie'),
        ('Joanna Wiguna', 'Annie'),
        ('Joe Yu', 'Joe'),
        ('Johanna Findeisen', 'Raizel'),
        ('Johnathan Lin', 'Oscar'),
        ('Johnny Stone', 'Paul'),
        ('Johnny Zhao', 'Paul'),
        ('Jonathan Karr', 'Joseph'),
        ('Jonathan Robbins', 'Jerome'),
        ('Joo Hee Eom', 'Annie'),
        ('Joseph Hernandez', 'Joe'),
        ('Josh Carbunck', 'Paul'),
        ('Josh Cherng', 'Walt'),
        ('Joshua Tjokrosurjo', 'Joe'),
        ('Josue Pacheco', 'Andrew'),
        ('Joy Herman', 'Hannah'),
        ('Joyce Low', 'Hannah'),
        ('Julia Chung', 'Hannah'),
        ('Julius Chang', 'Joseph'),
        ('Jun Heo', 'Jerome'),
        ('Jura Lin', 'Veronica'),
        ('Justin Washington', 'Andrew'),
        ('JZ Hung', 'Nikki'),
        ('Kaitlin Hairston', 'Raizel'),
        ('Karina Lozada', 'Annie'),
        ('Katya Becker', 'Annie'),
        ('Kayla Guilliams', 'Veronica'),
        ('Kaylin Wiseman', 'Nikki'),
        ('Keila Rios', 'Raizel'),
        ('Kelli Mann', 'Veronica'),
        ('Kenny Nguyen', 'Joseph'),
        ('Kenya Neal', 'Veronica'),
        ('Kevin Sung', 'Joseph'),
        ('Kevin Yum', 'Joseph'),
        ('Kimberly Seria', 'Hannah'),
        ('Kristie Ahn', 'Annie'),
        ('Kyle Yen', 'Jerome'),
        ('Laura Wilde', 'Nikki'),
        ('Liliana Marin', 'Raizel'),
        ('Lisa Matamoros', 'Hannah'),
        ('Lisa Welk', 'Raizel'),
        ('Lorena Roca', 'Hannah'),
        ('Luke Cui', 'Oscar'),
        ('Luke Lu', 'Jerome'),
        ('Lydia Lim', 'Annie'),
        ('Lydia Wong', 'Nikki'),
        ('Marian Sawada', 'Annie'),
        ('Mark Allijohn', 'Joe'),
        ('Mark Fan', 'Jerome'),
        ('Marvin Igwe', 'Jerome'),
        ('Mary Amelia Fichter', 'Annie'),
        ('Mary Strange', 'Raizel'),
        ('Matt Martin', 'Oscar'),
        ('Matthew Au', 'Oscar'),
        ('Matthew Lee', 'Andrew'),
        ('Mauricio Gonzalez', 'Walt'),
        ('Mayra Santiago', 'Raizel'),
        ('Megan Ku', 'Veronica'),
        ('Mercy Chi', 'Annie'),
        ('Micah Sy Lato', 'Andrew'),
        ('Michael Cofino', 'Joseph'),
        ('Michelle Liu', 'Hannah'),
        ('Michelle Nevarez', 'Annie'),
        ('Miles Mistler', 'Joseph'),
        ('Misael Trejo', 'Walt'),
        ('Natalie Lau', 'Raizel'),
        ('Natasha Schoenecker', 'Veronica'),
        ('Nathan Bodrug', 'Walt'),
        ('Nazarite Goh', 'Paul'),
        ('Nestor Zepeda', 'Oscar'),
        ('Nkhosi Gama', 'Joseph'),
        ('Nuria Dubon', 'Veronica'),
        ('Olivia Broussard', 'Veronica'),
        ('Paige Wheaton', 'Hannah'),
        ('Paul Wen', 'Andrew'),
        ('Peng Chen', 'Paul'),
        ('Peter Ho', 'Oscar'),
        ('Phoebe Lee', 'Nikki'),
        ('Preston Wang', 'Oscar'),
        ('Priscila Gonzalez', 'Hannah'),
        ('Priscilla Wang', 'Annie'),
        ('Priscilla Wong', 'Hannah'),
        ('Rachael Hernandez', 'Annie'),
        ('Rachel Ard', 'Nikki'),
        ('Rachel Chavana', 'Raizel'),
        ('Rafael Diaz', 'Joe'),
        ('Randy Juste', 'Joseph'),
        ('Raquel Morales', 'Nikki'),
        ('Raven Lester', 'Veronica'),
        ('Ray Ding', 'Jerome'),
        ('Rebecca Chao', 'Nikki'),
        ('Rebecca Huang', 'Veronica'),
        ('Rebecca Y. Chen', 'Annie'),
        ('Regina Suwuh', 'Raizel'),
        ('Rick Petkau', 'Joe'),
        ('Rina Liu', 'Raizel'),
        ('Rui Jiang', 'Paul'),
        ('Ruth Lee', 'Annie'),
        ('Ruth Liang', 'Hannah'),
        ('Ruth Long', 'Nikki'),
        ('Ruth Nan', 'Annie'),
        ('Ryan Armstrong', 'Joseph'),
        ('Ryan Holt', 'Walt'),
        ('Ryan Li', 'Joseph'),
        ('Sabrina Borunda', 'Nikki'),
        ('Sam Cummings', 'Oscar'),
        ('Samuel Duan', 'Paul'),
        ('Samuel Gutierrez', 'Paul'),
        ('Samuel Kwong', 'Joe'),
        ('Samuel Swei', 'Joe'),
        ('Samuel Yeh', 'Andrew'),
        ('Sandy Wang', 'Veronica'),
        ('Sarah Chen', 'Veronica'),
        ('Sarah Lin', 'Annie'),
        ('Sean David', 'Andrew'),
        ('Sebrina Yan', 'Veronica'),
        ('Selcy Borromeo', 'Veronica'),
        ('Serena Lee', 'Nikki'),
        ('Serina X. Lee', 'Annie'),
        ('Shannon Wong', 'Nikki'),
        ('Shaun Pan', 'Paul'),
        ('Shea Braddock', 'Veronica'),
        ('Sheryl Pu', 'Hannah'),
        ('Shirleen Fang', 'Raizel'),
        ('Shula Yuan', 'Raizel'),
        ('Sierra Shepard', 'Raizel'),
        ('Silvia Coto', 'Hannah'),
        ('Sophia He', 'Nikki'),
        ('Sophia Xu', 'Veronica'),
        ('Sophie Chen', 'Nikki'),
        ('Stacy Castillo', 'Veronica'),
        ('Stephanie Azubuike', 'Raizel'),
        ('Stephanie Chukwuma', 'Nikki'),
        ('Stephanie Wang', 'Nikki'),
        ('Stephen Kwan', 'Andrew'),
        ('Susan Cheng', 'Veronica'),
        ('Susanna Bruso', 'Annie'),
        ('Sven Lee', 'Joe'),
        ('Tae Suh', 'Raizel'),
        ('Tammi Hua', 'Raizel'),
        ('Tanya Bae', 'Nikki'),
        ('Taylor Cole', 'Hannah'),
        ('Tiffaney Tatro', 'Annie'),
        ('Tiffany Chua', 'Veronica'),
        ('Tiffany Liu', 'Annie'),
        ('Tina Chang', 'Annie'),
        ('Titus Ting', 'Jerome'),
        ('Tobi Abosede', 'Annie'),
        ('Tommy Lockwood', 'Joe'),
        ('Ty Wilson', 'Joseph'),
        ('Vera Zhao', 'Raizel'),
        ('Victoria Hung', 'Veronica'),
        ('Vorah Shin', 'Raizel'),
        ('Will Wang', 'Walt'),
        ('William Jeng', 'Joe'),
        ('Xuefei Zheng', 'Hannah'),
        ('Yang Cheng', 'Raizel'),
        ('Yi Sun', 'Andrew'),
        ('Yuan Le', 'Raizel'),
        ('Zhen Wang', 'Hannah'),
        ('Zoe Zhang', 'Veronica'),
    ]

    for tat in trainees_to_tas:
      ta = User.objects.filter(firstname=tat[1], type='T').first()

      fname, lname = tat[0].split(' ', 1)
      Trainee.objects.filter(firstname=fname, lastname=lname).update(TA=ta)

    currentterm = Term.objects.get(current=True)
    Trainee.objects.filter(is_active=True).update(date_end=currentterm.end)
    for t in Trainee.objects.filter(is_active=True):
      t.terms_attended.add(currentterm)

    lastterm = Term.objects.get(year=currentterm.year - 1, season='Fall')
    for t in Trainee.objects.filter(current_term__gte=2):
      t.terms_attended.add(lastterm)
      t.date_begin = lastterm.start
      t.save()

    twoterms_ago = Term.objects.get(year=currentterm.year - 1, season='Spring')
    for t in Trainee.objects.filter(current_term__gte=3):
      t.terms_attended.add(twoterms_ago)
      t.date_begin = twoterms_ago.start
      t.save()

    threeterms_ago = Term.objects.get(year=currentterm.year - 2, season='Fall')
    for t in Trainee.objects.filter(current_term=4):
      t.terms_attended.add(threeterms_ago)
      t.date_begin = threeterms_ago.start
      t.save()

  def handle(self, *args, **options):
    Trainee.objects.all().delete()
    print("* Populating trainees...")
    self._create_trainees()