# GitHub Wiki
Important notes on the GitHub Repository and handling the Code.


### Working with git and GitHub
GitHub can make our lives working on the project significantly easier.
It allows us to keep all our code online in one place, while being able to 
easily work on different parts of it and collaborate with other people.


### Branches
The idea of "branching up" the project repository is an important aspect of
working with GitHub, and will allow us to seamlessly integrate code that was 
independently developed by different people for different tasks.

When we create a new "Branch" of our GitHub repository, you can imagine this 
as if we would create a new copy of the entire repository. In this new "copy" 
of the code, you can try stuff, mess around, and write new code aiming to 
add new functionality to our repository.

This also means that we need to have one big main branch, which is the starting 
point for the other branches and also can be seen as the current total working 
version of our code. This branch is called the **master branch** in GitHub. 
Since this branch is our main point of reference, you should pretty much 
**never edit the master branch directly** while working on the repository.


### The general workflow explained
Instead of directly changing the code saved in our master branch,
the usual working procedure goes as follows:

1. **Branch**: You create a new branch for a specific task or to try out new things.
2. **Edit**: You edit **your branch** as you like it.
3. **Merge**: If you think that your code is working and should be integrated into 
    the master branch, you first check that your branch is compatible with the current 
    master branch. This process is called *merging*. It may be that while you worked on 
    your own branch, someone else *pushed* a *commit* to the master branch, which means 
    that the code you got at the moment does not include the changes the other person 
    contributed to the master branch.
     
    During the *merging* process you go through the 
    code and check if there are no conflicts between your branch and the master branch, 
    and that the resulting code will be good to go and work fine, as it will be used as 
    the common reference point for all contributors from this point. This sounds 
    scarier than it actually is. Most of the time, you won't face any problems while 
    merging. However, there is the potential to seriously mess up the code and generally 
    it is a good idea to relay the merging process to more experienced users if you're 
    not that familiar with the code and/or GitHub.


### Introduction into the working process
In the following, you can read a short introduction into the general GitHub workflow and
the most important commands you will need during the process.

For most of the actions described here, there are alternative (and often easier) ways
either on the GitHub page, or in your Integrated Development Interface (Atom or Pycharm).
For the sake of comprehensiveness, I'll explain all actions using the command line.
However, you can check if your IDE provides a simpler interface for working with github.
The procedures themselves (i.e. the important part) will stay the same for both.

- #### Clone the repository
    First you "clone" the repo. This means you create a physical copy of the online GitHub
    code on your laptop.
    For this purpose, you open your computer's command line. Then you direct to the folder 
    where you want to store the repository:
    ```shell script
    $ cd /path/to/repository
    ```
    Then you clone the repository, using the URL provided from our repository's page:
    ```shell script
    $ git clone https://github.com/DiGyt/NBP_Hyperscanning.git
    ```
    Now you got a full copy of the repository in the respective folder.
    
- #### Create a new branch
    Now you create a new branch where you can work on and change stuff.
    ```shell script
    $ git branch my_new_branch
    ```
  
- #### Switch branches
    Before you start coding, you must switch to the branch you want to edit. This is 
    important, as it can happen that you accidentally edit the master (or some other) 
    branch that you do not want to edit. You can use the `checkout` command to switch
    between branches.
    ```shell script
    $ git checkout my_new_branch
    ```
    Now you can edit your new branch. With `git checkout`, you can flexibly switch 
    between different branches while developing, for example when you're working on
    different tasks at the same time. However, it is good advice to "save" your commits 
    to each branch, before switching to another (as explained in the next step).
    
- #### Commit
    Commiting broadly means "saving" the progress you made on a specific branch. When 
    you commit a file, your current branch will save all the changes you made to this 
    file. This is a neccessary step you need to take before *pushing* (~uploading) your 
    progress to the online repository. While working on a specific branch, you can 
    commit edited files to that branch with:
    ```shell script
    $ git commit file_xy.py
    ```
    After running the command, you can add a commit message to state which changes you 
    undertook in the respective commit.
  
- #### Pulling and Pushing
    In order to synchronize the code between the repository cloned locally on your computer 
    and the remote repository on GitHub, you need commands to exchange between both. There 
    are two commands to do this, which are `pull` and `push`.
    
    Pulling means that you get the code from the remote repository, and fill it into your 
    locally saved repository clone. This makes sure that your code is up-to-date with the 
    remote repository and generally should be done often.
    ```shell script
    $ git pull origin my_new_branch
    ```
  
    Pushing means that you take the (edited) code from your locally cloned repository, 
    and add it to the remote/online GitHub repository. When you push, all changes made 
    to a local branch will be added to the respective remote branch. This means when you 
    push your local branch `my_new_branch`, the local changes will be added to the online 
    version of `my_new_branch` (or the entire branch added if it doesn't exist yet).
    ```shell script
    $ git push origin my_new_branch
    ```
    
    Usually if you're working on a branch that is already present in the remote repository, 
    simply writing `git pull` or `git push` will suffice.
  
- #### Merging/ Pull Requests
    When all the work is done in your branch and you want to merge the code in this branch 
    into another branch, use `merge`. When merging, it is good advice to perform `git pull` 
    on each branch first to make sure that your branches are up-to-date with their remote 
    counterparts.
    ```shell script
    $ git checkout branch_to_merge_in
    $ git merge my_new_branch
    ```
    Please **do not merge into the master branch** directly. Instead, you can open a "Pull 
    Request", which basically is an online form or proposal to merge one branch into the 
    master (or any other) branch. With this method, other contributors are able to check 
    your code and validate if it is ready to be merged into the master branch.
    
    If you want to merge into the master branch, go to the 
    [Repository](https://github.com/DiGyt/NBP_Hyperscanning), then click on 
    [Pull Requests](https://github.com/DiGyt/NBP_Hyperscanning/pulls) and on 
    [New pull request](https://github.com/DiGyt/NBP_Hyperscanning/compare).
    Now you can choose which branch to merge into which branch and submit your pull 
    request. On the submission page, you can describe the changes you added to your 
    branch. You also can assign the Pull Request to another contributor which means that 
    the Pull Request can only be merged if this contributor has seen it and approves.
    
And that's pretty much everything you need to successfully work with GitHub!