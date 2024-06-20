# tau-project-template

Template for CSC 453 Projects

## Initialization

#### Fetching the shared code

After your repository is created, you need to run the following command from the repo's top-level directory to fetch the code from shared repositories:

```bash
./init.sh
```

After that, you will see four new directories:

1. `tau` - The shared code for the project
2. `rdgen` - The parser generator
3. `testerator` - The test driver
4. `vm` - The virtual machine your compilers will target

**DO NOT RUN THIS COMMAND MORE THAN ONCE!**

#### Generating the stub files

Projects begin with a set of files that are auto-generated.  They are generated with the following command:

```bash
./tau/utilities/initialize.sh
```

(That script is a linux/MacOS command.)

After that, you will see the stubs for the eight (8) files that you will turn in for every milestone:

1. `scanner.py`
2. `parse.py`
3. `assign.py`
4. `bindings.py`
4. `offsets.py`
5. `typecheck.py`
6. `codegen.py`
7. `tau.ebnf`

## Updates

Shared code may need updating from time to time.  That is done with the following command:

```bash
./update.sh
```
