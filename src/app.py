from yaml import load
from pathlib import Path
import os
import inquirer
import shutil


try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class utm:
    def __init__(self) -> None:
        self.local_path_check = [
            Path(str(Path.home()) + "/.utm/template"),
            Path("/usr/share/utm/templates"),
            Path("./templates"),
        ]
        self.local_path = []
        for path in self.local_path_check:
            if not path.exists():
                try:
                    os.makedirs(path.resolve())
                except Exception as e:
                    print(f"Error for {path.resolve()}: {e}")
                    continue
            self.local_path.append(path)

        self.templateNum = 0
        self.projectName = ""
        self.templateList = []
        self.templateTranslator = {}
        self.getAllTemplates()
        self.displayChoices()
        self.importTemplate()

    def displayChoices(self):
        data = []
        for desc in self.templateList:
            data.append([
                desc["name"],
                desc["description"] if len(desc["description"]) <= 200 else desc["description"][:197] + '...',
                        [tag + ", " for tag in desc["tags"]]
                    ])
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
            self.projectName = userNameChoice
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
                        desc["location"] = Path(template).resolve()
                        self.templateList.append(desc)
                        self.templateTranslator[desc["name"]] = compt
                    compt += 1
    def importTemplate(self):
        if self.projectName == "":
            print("Bad project name")
            exit(1)
        try:
            shutil.copytree(self.templateList[self.templateNum]["location"], f"./{self.projectName}", ignore=shutil.ignore_patterns('template_description.yaml'))
        except:
            print("Failed to create the new project...")

        pass
utmanager = utm()
