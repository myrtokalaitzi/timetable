import csp
import pandas as pd
import time
from utils import F 
from collections import namedtuple

# Ορισμός του namedtuple για το μάθημα
Course = namedtuple('Course', ['name', 'semester', 'professor','difficulty', 'lab'])

class Timetable(csp.CSP):
    def __init__(self, df):
        # Αρχικοποίηση των μελών της κλάσης
        self.variables = []
        self.domains = {}
        self.courses = []  # Λίστα που θα κρατά τα αντικείμενα Course
        self.neighbors = dict()
        self.counter = 0  # ποσες φορες κληθηκε η constraints

        # Διαβάζουμε τα δεδομένα από το DataFrame
        for _, row in df.iterrows():
            # Δημιουργία του αντικειμένου Course για κάθε μάθημα
            course = Course(
                name=row['Μάθημα'],
                semester=row['Εξάμηνο'],
                professor=row['Καθηγητής'],
                difficulty=row['Δύσκολο (TRUE/FALSE)'],
                lab=row['Εργαστήριο (TRUE/FALSE)']
            )

            # Προσθετουμε το μάθημα στη λίστα μεταβλητών
            self.variables.append(course.name)

            # Προσθετουμε το μάθημα στη λίστα courses
            self.courses.append(course)

            # Δημιουργια domains
            self.domains[course.name] = [(x, y) for y in range(1, 22) for x in range(1, 4)]

        # Ολα τα μαθηματα ειναι γειτονικα για το καθενα
        for var in self.variables:
            self.neighbors[var]=[]
            for var1 in self.variables:
                if var1!=var:
                    self.neighbors[var].append(var1)

        csp.CSP.__init__(self,self.variables, self.domains, self.neighbors, self.constraints)        

    # Συναρτηση για να εχουμε προσβαση στο tuple απο το ονομα
    def get_course_by_name(self, name):
        for course in self.courses:
            if course.name == name:
                return course
    
    def constraints(self, A, a, B, b):
        self.counter += 1
        course1 = self.get_course_by_name(A)
        course2 = self.get_course_by_name(B)

        #Υπάρχει μόνο μία αίθουσα διαθέσιμη για τις εξετάσεις
        if a[1] == b[1] and a[0] == b[0]:
            return False

        # Τα μαθήματα του ίδιου εξαμήνου θα πρέπει να εξετάζονται σε διαφορετικές ημέρες.
        if course1.semester == course2.semester and a[1] == b[1]:
            return False
        
        #Μαθήματα του ίδιου καθηγητή πρέπει να εξετάζονται σε διαφορετικές μέρες
        if course1.professor == course2.professor and a[1] == b[1]:
            return False
        
        # Οι εξετάσεις δύσκολων μαθημάτων πρέπει να απέχουν τουλάχιστον 2 ημέρες μεταξύ τους
        if course1.difficulty == True and course2.difficulty == True:
            if abs(a[1] - b[1]) < 2:
                return False

        if a[1] == b[1]:
                #δε γινεται να εξεταστουν δυο μαθηματα με εργαστηριο την ιδια μερα γιατι δεν αρκουν τα slots
                if course1.lab == True and course2.lab == True:
                    return False
                #εξέταση του εργαστηρίου, η οποία θα πρέπει να ακολουθεί αμέσως μετά την εξέταση της θεωρίας την ίδια ημέρα   
                elif course1.lab == True:
                    if a[0] == 3:
                        return False
                    elif b[0] == a[0] + 1:
                        return False
                #το ιδιο για το 2ο μαθημα
                elif course2.lab == True:
                    if b[0] == 3:
                        return False
                    elif a[0] == b[0] + 1:
                        return False
        
        return True

    

    def display_all(self, assignment):
        print('The program is: ')
        if assignment is None:
            print('limit has been passed')
        else:
            for y in range(1, 22):
                print( "-" * 50,)
                print(f'Ημέρα {y}:')
                slots = {x: "-" for x in range(1, 4)}  # Προετοιμάζουμε τα slots ως κενά
                for var in self.variables:
                    if assignment[var][1] == y:  # Ελέγχουμε αν το μάθημα είναι στη συγκεκριμένη ημέρα
                        x, _ = assignment[var]
                        slots[x] = var  # Τοποθετούμε το μάθημα στο αντίστοιχο slot
                        # Έλεγχος αν το μάθημα έχει εργαστήριο
                        course = self.get_course_by_name(var)
                        if course.lab:
                            slots[x + 1] = var + ' LAB'

                # Εκτυπώνουμε τα slots
                for x in range(1, 4):
                    print(f'  Slot {x}: {slots[x]}')
            print('-' * 50)
            
#   main

if __name__ == '__main__':
    df = pd.read_csv('h3-data.csv')
    t = Timetable(df)
    begin = time.time()

    # m = csp.backtracking_search(t, csp.mrv, csp.lcv, csp.mac)
    
    # m = csp.backtracking_search(t, csp.dom_wdeg, csp.lcv, csp.mac)

    # m=csp.backtracking_search(t, csp.mrv, csp.lcv, csp.forward_checking)

    
    m=csp.backtracking_search(t, csp.dom_wdeg, csp.lcv, csp.forward_checking)
    
    
    # m=csp.backtracking_search(t)

    # m=csp.backtracking_search(t , csp.mrv)

    # m=csp.min_conflicts(t)

    end=time.time()

    t.display_all(m)
    print('constraints function was called: '+ str(t.counter))
    print()
    print('time: '+ str(end-begin) )
    print()
    print('total number of assignments:' + str(t.nassigns))

