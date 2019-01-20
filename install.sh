echo 'Making executable..'
chmod +x main.py
echo 'Linking to local binary directory..'
echo $(pwd)/main.py
ln -s $(pwd)/main.py /usr/local/bin/pocketsnack
echo 'checking for Python3...'
if [ $(which python3) ]; then
  echo 'Python 3 is installed and python3 command works'
  echo 'Installation complete ✅ You can now get started!'
  echo '------------------------------------------'
  # check if user wants to just authorise straight away
  echo 'Do you want to authorise your app with Pocket now? Choose 1 for Yes or 2 for No'
  select response in Yes No
  do
    case $response in
      Yes) 
        pocketsnack authorise
          exit 0
      ;;
      No) 
        echo 'Run "pocketsnack authorise" when you are ready to authorise your app.'
        exit 0
      ;;
      *) 
        echo 'Enter "1" to authorise or "2" to exit.';;
    esac
  done
else
  echo '❌  Python 3 must be installed and called by "python3"'
fi