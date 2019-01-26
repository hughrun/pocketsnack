#!/usr/bin/env bash
echo 'Making executable..'
chmod +x main.py
echo 'Linking to local binary directory..'
ln -s $(pwd)/main.py /usr/local/bin/pocketsnack
echo 'checking for Python3...'
if [ $(which python3) ]; then
  echo 'Python 3 is installed and python3 command works'
  echo 'Installation complete ✅ You can now get started!'
  echo '-------------------------------------------------'
  # check if user wants to just authorise straight away
  echo 'Do you want to authorise your app with Pocket now? Choose 1 for Yes or 2 for No'
  select response in Yes No
  do
    case $response in
      Yes)
        echo 'Authorise pocketsnack in the browser window that opens in a moment, then return to this command line to finish setting up.'
        sleep 5s
        pocketsnack authorise
          # here we should ask if they want to set up a regular job
        echo 'Do you want to automatically refresh your Pocket List? This will run "stash" and then "lucky_dip" once per day.'
        select daily in Yes No
        do
          case $daily in
            Yes)
              # what hour do they want to refresh their list? Must be a number between 0 and 23. Is 6 by default.
              echo 'Enter an hour between 0 and 23 for when you want to run your script.'
              read hour            
              isnum='^2[0-3]$|^1?[0-9]$'
              while ! [[ $hour =~ $isnum ]]
              do
                echo 'Invalid choice - please enter a whole number between 0 and 23'
                read hour
              done
              echo "you chose $hour"
              # are they running MacOS or Linux
              echo "Ok last question: are you running (1) MacOS or (2) Linux?"
              select operating_system in MacOS Linux
              do
                case $operating_system in
                  MacOS)
                    # create a new plist file with the hour number and put it in the right place
                    sed "22 s/[0-9][0-9]*/$hour/" <hourly.plist >~/Library/LaunchAgents/com.getpocket.pocketsnack.plist
                    # load launchd file
                    launchctl load ~/Library/Launchagents/com.getpocket.pocketsnack.plist
                    echo "You're all set up! Enjoy your new Pocket experience."
                    exit 0
                    ;;
                  Linux)
                    # edit crontab
                    (crontab -l ; echo "0 $hour * * * /usr/local/bin/pocketsnack refresh") 2> /dev/null | sort | uniq | crontab -
                    echo "You're all set up! Enjoy your new Pocket experience."
                    exit 0
                    ;;
                  *)
                    echo "Please select 1 for MacOS or 2 for Linux"
                    ;;
                esac
              done
              ;;
            No)
              echo 'No script scheduled. You can use pocket-snack manually at any time using the pocketsnack command.'
              exit 0
              ;;
            *)
              echo 'Please select 1 to schedule daily refreshes or 2 to exit.'
              ;;
          esac
        done
        ;;
      No) 
        echo 'Run "pocketsnack authorise" when you are ready to authorise your app.'
        exit 0
        ;;
      *) 
        echo 'Enter "1" to authorise or "2" to exit.'
        ;;
    esac
  done
else
  echo '❌  Python 3 must be installed and called by "python3"'
fi