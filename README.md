# Stash plugin: Performer Cleanup

This is a plugin for stash. It adds a `cleanup performers` task. 
This task processes all none org scenes and removes preformers who's name is shorter and are included in co-performers name.

example: Jane, Jane Doe

will remove Jane, leaving only Jane Doe

# How to set it up

Add the python files too your `.stash/plugins` directory

create a `virtualenv`

```bash
virtualenv -p python3 --system-site-packages ~/.stash/plugins/env
source ~/.stash/plugins/env/bin/activate
pip install ~/.stash/plugins/requirements.txt
```

# How to use

Rescan the plugins, you will find a new button in the `Tasks` sections in the settings.

