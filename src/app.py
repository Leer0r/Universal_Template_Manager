from yaml import load
from pathlib import Path
import os
import sys
import inquirer
import shutil


try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import json

manPage = """
UTM: Universal Template Manager
Store and restore all your template from any language

Usage : utm [import | export] [-U | -R] or utm -H

import : import a template from local or remote source
export : export template to local or remote folder

-U (require sudo):
    import : Add /usr/share/utm/template to the template path
    export : export the new template in /usr/share/utm/template

-R:
    import : seach template to the remote repos
    export : export template to the remote repos

    If multiple repos are set, you can select a specific one with -R <Link to the remote repos>. By default, it link to the global repos dns

-H:
    Display usage instruction (this message)
"""


class utm:
    def __init__(self, usr=False, remote=False, remoteLink="") -> None:
        self.confPath = Path(str(Path.home()) + "/.utm/config.json").resolve()
        homedir = Path(str(Path.home()) + "/.utm").resolve()
        if not homedir.exists():
            try:
                os.makedirs(homedir.resolve())
            except:
                print(f"Failed to create utm folder at {homedir}")
                exit(1)

        confPath = Path(homedir / "config.json")
        if not confPath.exists():
            self.writeBaseConfig()

        if (usr):
            if (os.geteuid != 0):
                print("Using -U need sudo privilege")
                exit(1)
        pass

    def writeBaseConfig(self):
        config = {
            "remoteLink": [
                "utm.coffeebreaks.eu",
                "utmsave.coffeebreaks.eu"
            ]
        }
        try:
            with open(self.confPath, "w") as configFile:
                configFile.write(json.dumps(config))
        except Exception as e:
            print(f"Failed to create configFile at {self.confPath}")
            print(e)

    def loadConf(self):
        conf = {}
        try:
            with open(self.confPath, "r") as confFile:
                return json.loads(confFile.read())
        except:
            print('Failed to load conf file')
            exit(1)
        return {}


class utm_import(utm):
    def __init__(self, usr=False, remote=False, remoteLink="") -> None:
        super().__init__(usr, remote, remoteLink)
        self.localConfig = self.loadConf()
        self.local_path_check = [
            Path(str(Path.home()) + "/.utm/template"),
            Path("./templates"),
        ]
        if (usr):
            self.local_path_check.append(Path("/usr/share/utm/templates"))
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
                desc["description"] if len(
                    desc["description"]) <= 200 else desc["description"][:197] + '...',
                [tag + ", " for tag in desc["tags"]]
            ])
        question = [
            inquirer.Text("project_name",
                          message='Nom du nouveau projet',
                          autocomplete=True),
            inquirer.List("tempalte",
                          message='Quel template voulez vous ?',
                          choices=[data[i][0] for i in range(len(data))],
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
            print(
                f"Création du projet {userNameChoice} avec {userTemplateChoice} ...")

        except KeyError as e:
            print("Error : template not found")
            exit(1)

    def getAllTemplates(self):
        compt = 0
        for path in self.local_path:
            for template in path.iterdir():
                description = template / "template_description.yaml"
                if (description.exists()):
                    with open(description.resolve(), "r") as f:
                        desc = load(f.read(), Loader)
                        desc["location"] = Path(template).resolve()
                        self.templateList.append(desc)
                        self.templateTranslator[desc["name"]] = compt
                    compt += 1

    def importTemplate(self):
        if self.projectName == "":
            print("Bad project name")
            exit(1)
        try:
            shutil.copytree(self.templateList[self.templateNum]["location"],
                            f"./{self.projectName}", ignore=shutil.ignore_patterns('template_description.yaml'))
        except:
            print("Failed to create the new project...")
        pass


class utm_export(utm):
    def __init__(self, usr=False, remote=False, remoteLink="") -> None:
        super().__init__(usr, remote, remoteLink)
        self.currentDirectory = Path.cwd().resolve()
        self.currentDirectoryDescriptionFile = Path(
            self.currentDirectory / "template_description.yaml")
        self.templateName = self.currentDirectory.name

    def createTemplateDescriptionFile(self):
        try:
            with open(self.currentDirectoryDescriptionFile, 'w') as descriptionFile:
                description = {
                    "name": self.templateName,
                    "description": "",
                    "tags": []
                }

                descriptionFile.write(description)
        except Exception as e:
            print(
                "Failed to create template_description.yaml, please check folder privileges")
            exit(1)

    def initTemplate(self):
        if not self.currentDirectoryDescriptionFile.exists():
            print(
                f"Create base template description in {self.currentDirectory}")
            self.createTemplateDescriptionFile()

    def addTemplateTag(self):
        questions = [
            inquirer.Text("project_tag", "Quel tag pour ce template ?")
        ]

        awnser = inquirer.prompt(questions)
        projectTag = awnser["project_tag"]


if len(sys.argv) == 1:
    print(manPage)
    exit(0)

if sys.argv[1] == "import":
    utmanager = utm_import

elif sys.argv[1] == "export":
    utmanager = utm_export

elif sys.argv[1] == "-H":
    print(manPage)
    exit(0)

else:
    print("First argument unknown")
    print(manPage)
    exit(0)

usr, remote = False, False
remoteLink = ""
argTab = sys.argv[2:]
while argTab:
    arg = argTab[0]
    if arg == "-U":
        usr = True
    elif arg == "-R":
        remote = True
        if (len(argTab) > 1 and argTab[1][0] != '-'):
            remoteLink = argTab[1]
            del argTab[1]
    else:
        print(f"Error, unknown argument {arg}")
        print(manPage)
        exit(1)
    del argTab[0]

utmanager(usr, remote, remoteLink)
