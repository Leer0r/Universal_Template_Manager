# UTM: Universal Template Manager
Store and restore all your template from any language
# Usage
utm [import | export] [-U | -R] or utm -H
- import : import a template from local or remote source
- export : export template to local or remote folder
- -U (require sudo):
   - import : Add /usr/share/utm/template to the template path
   - export : export the new template in /usr/share/utm/template
- -R:
  - import : seach template to the remote repos
  - export : export template to the remote repos
  If multiple repos are set, you can select a specific one with -R <Link to the remote repos>. By default, it link to the global repos dns
- -H:
  Display usage instruction
