#Setting up run anywhere programs

Firstly all the pythoon scripts need this line:
#!/usr/bin/env python3

I wrote a script to add that called fix_shebangs.sh

to run this of course, as usual:
chmod +x ./fix_shebangs.sh

Then all the files in this entire repository need to be set to executable
... I think "fix_shebangs.sh does that too....


Then add all the paths to the PATH, if not already:

for dir in "$HOME/LGithub/Python-Utilities"/*/; do
	PATH="$dir:$PATH"
done

but obviously get the path right!

Noticed github will ruin this so try this to preserve the executableness
(type of thing)
git update-index --chmod=+x run_model_593.sh
git commit -m "Fix: make script executable"


