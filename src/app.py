from yaml import load
from pathlib import Path
import os
from columnar import columnar
import inquirer


try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class utm:
    def __init__(self) -> None:
        self.local_path_check = [
            Path("/usr/share/utm/templates"),
            Path("./templates")
        ]
        self.local_path = []
        for path in self.local_path_check:
            if not path.exists():
                try:
                    os.makedirs(path.resolve())
                except Exception as e:
                    print(f"Error for {path.resolve()}: no directory")
                    continue
            self.local_path.append(path)
                    
        self.templateNum = 0
        self.templateList = []
        self.templateTranslator = {}
        self.getAllTemplates()
        self.displayChoices()

    def displayChoices(self):
        data = []
        for desc in self.templateList:
            data.append([
                desc["name"],
                desc["description"] if len(desc["description"]) <= 200 else desc["description"][:197] + '...',
                        [tag + ", " for tag in desc["tags"]]
                    ])
        print(data)
        question = [
            inquirer.Text("project_name",
                          message='Nom du nouveau projet',
                          autocomplete=True),
            inquirer.List("tempalte", 
                          message='Quel template voulez vous ?',
                          choices= [data[i][0] for i in range(len(data))],
                          carousel=True,
                        default=data[0][0])
        ]
        awnser = inquirer.prompt(question)
        if awnser == None:
            print("Action canceled")
            exit(1)
        try:
            userTemplateChoice = awnser["tempalte"]
            userNameChoice = awnser["project_name"]
            self.templateNum = self.templateTranslator[userTemplateChoice]
            print(f"Création du projet {userNameChoice} avec {userTemplateChoice} ...")
        except KeyError as e:
            print("Error : template not found")
            exit(1)
        

    def getAllTemplates(self):
        compt = 0
        for path in self.local_path:
            for template in path.iterdir():
                description = template / "template_description.yaml"
                if(description.exists()):
                    with open(description.resolve(), "r") as f:
                        desc = load(f.read(),Loader)
                        self.templateList.append(desc)
                        self.templateTranslator[desc["name"]] = compt
                    compt += 1
utmanager = utm()
