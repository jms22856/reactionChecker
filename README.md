# Autocatalysis Wrapper

Mutual autocatalysis is the requirement that every species in a reaction network must influence and be influenced by another species in the network. Species A influences species B if a change in the concentration/amount of A causes a change in species B's kinetics. Mutual autocatalysis is a necessary requirement for the [Basic Pathways Framework](https://pubmed.ncbi.nlm.nih.gov/38161422/).

This program checks that all species in a provided reaction network follow mutual autocatalysis. This is done using a species-species directed graph, where edges represent influence. Checking that all species have an indgree and outdegree of at least one ensures mutual autocatalysis.

The app is a quick tk wrapper around the program functions, which are found in helper. The template for the frontend was created using Claude Sonnet 4.6, which was then modified to suit our lab's specific requirements. The app.exe file was packaged using pyinstaller.

# Get Started
Go the releases, and download app.exe.

Alternately, clone the repo, install the required python packages (should just be networkx) and run app.py.