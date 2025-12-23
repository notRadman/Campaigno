# Hemmah
Simple campaign manager for unix like systems.

IN THE NAME OF GOD, THE MOST GRACIOUS, THE MOST MERCIFUL.

Here is the Hemmah app which makes your productivity slope like waves of 6 weeks of work and 2 weeks of rest, not sure of it, but I have the freedom to try it.

Using the program as follows:
    python3 hemmah.py <tag>
        you can see available tags by typing <python3 hemmah.py> or <python3 hemmah.py help>, that help is in arabic, cope with it if you aren't.
        you can set its keys (for templates) and default apps from it.

    hemmah-prompt.sh
        that prints little piece of information about the current status you can use it in your bar, terminal, etc.

In the begining you will find the the folder contains: hemmah.py, hemmah-prombt.sh and that Readme file.

You have to make campaigns file for the first time and you have to set its path inside the program, you alse have to set keys to give some support to your language like me, then in the campaigns.md file you have to set template for campaigns.
That template should be equal to the keys you set. here is some notes you need to know:
    - tasks and links should be like that (tab then -((iam not sure if you have to type tab)))
    - tasks can be [ ] for hanging or active tasks, [x] for the completed tasks, [-] for canceled ones.
    -the program has no work to do with status, rate and drafts, those are for you.
    -date should be written in YYYY-MM-DD format
    -campaigns should start and end with ---, that's too important.
    -templates should has ###TEMPLATE### after ---
here is the default theme:
    ```
        ---
        ###TEMPLATE###
        number:
        name:
        description:
        start: yyyy-mm-dd 
        end: yyyy-mm-dd
        recovery-end:
        milestones:
           - [x] completed
           - [-] canceled
           - [ ] active or hanged 
        status:
        rate:
        links&drafts:
           -
        ---
    ```

There is some additional files you can create, one is wiki.pdf which you type why this method is good for you, another one is yourself.md which you type something you wanna tell yourself and the last additional one is quotes.md which you put phrases that motivates you and the app choose from those lines randomly.

That's the end, stay smart, tell me if you find bugs or have improvements.
