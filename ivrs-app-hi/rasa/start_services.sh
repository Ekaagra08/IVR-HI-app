#cd app/
cd ./app
# Start rasa server with nlu model
rasa run --model models/nlu-20220513-082944.tar.gz --enable-api --cors "*" --debug \
         -p 5005