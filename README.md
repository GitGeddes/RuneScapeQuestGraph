# RuneScape Wiki Scraper
Build connected graphs for any number of quests in the game, between 1 and all quests!

# New Features!
  - Updated links to the new Old School RuneScape wiki!
  - Updated quest requirement-finder to reflect new website's structure!
  - Added this README!

## Main Features:
  - Pull all quest names and their respective URLs from the RuneScape wiki.
  - Traverse through each quest page and add all listed quest requirements.
  - Save a local copy of the quest list, including requirements, to avoid the long process of pulling data from the website.
    - Delete the file *quests.txt* if you want to reload the list.
  - Add any new quests that get released, even after this script was written.
  - Plot a graph using Matplotlib with quest names on each node and lines connecting quests to their requirements and open this graph in a new window. (Only opens embedded window in PyCharm 2018.2.4)
  - Output a *png* file that looks a lot better than the Matplotlib graph.
  - Inform the user of the quest with the tallest tree structure. (Not the largest number of requirements)

You can also modify the Python file and un-comment the quests at the bottom to show one quest or just a few.
Or edit those lines and add other quests you might want to look at.
### Tools Used

* Python 2.7
* [graphviz] 2.38
* [PyGraphviz] 1.3.1 for Python 2.7
* BeautifulSoup
* Matplotlib
* Mechanize
* NetworkX

### Installation
###### This script was built and tested on Python 2.7 on the Windows 10 operating system using the PyCharm IDE.

* Firstly, install **Python 2.7** and make sure that the installation folder is in your Windows PATH.
* Download the **Graphviz 2.38** installer from the [graphviz] website. Follow the on-screen instructions.
After it finishes, add the folder "Graphviz2.38/bin" to your Windows PATH.
[Here's how to add programs and folders to your Windows PATH.](https://www.howtogeek.com/118594/how-to-edit-your-system-path-for-easy-command-line-access/)
* As of writing this, **PyGraphviz** has issues when trying to install it using the Python *pip* installer.
Instead, go to this link: [PyGraphviz] and download the corresponding wheel file for your platform. For example, I am running Python 2.7 on a 64-bit Windows machine, so I would download "pygraphviz-1.3.1-cp27-none-win_amd64.whl"
To install this wheel, run the command (using your corresponding file):
```sh
$ pip install pygraphviz-1.3.1-cp27-none-win_amd64.whl
```
* For the other 4 Python Libraries (BeautifulSoup, Matplotlib, Mechanize, and NetworkX), you should be able to simply install them using the *pip* installer.
```sh
$ pip install beautifulsoup4
$ pip install matplotlib
$ pip install mechanize
$ pip install networkx
```
* If installing any of these libraries through *pip* does not work, then try it in the PyCharm Interpreter Settings.

### Usage
* **PyCharm IDE**: Simply download the repository (you really only need the Python file) and install all of the libraries to a Python 2.7 environment. Then the script can be run inside of PyCharm. The current version of PyCharm (2018.2.4) does not open the Matplotlib graph in a new window, instead it opens the plot in an embedded window inside the IDE. This could either be that I'm running the paid version of PyCharm or this feature changed earlier in 2018.
* **Windows Console**: I have had trouble getting the Windows PATH working properly, but I was able to run the script using the Administrator Command Prompt for Windows. I also had to explicitly run the python.exe in the Python 2.7 installation folder. However, using the console opens a new window for the Matplotlib graph rather than PyCharm's embedded window. The benefits of this is that the standalone window can be resized to space the quest labels out and become more readable.

Delete the file *quests.txt* to reload the quest list from the website. Do this any time that a new quest is released, or if you want to see the script in action.

### Todos

 - Allow for either command-line or GUI input for either all quests or individual quests.

License
----

MIT

[//]: # (This Readme file was made using dillinger.io)

   [graphviz]: <http://www.graphviz.org/download/>
   [PyGraphviz]: <https://www.lfd.uci.edu/~gohlke/pythonlibs/#pygraphviz>
