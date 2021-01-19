#Class to hold variables of status
class Configuration:
    #Variable that indicates if a name is chosen. If it is, it won't fall into the answer_name_intent
    name_exists = False

    def set_name_exists(value):
        name_exists = value
        
    def get_name_exists():
        return name_exists
