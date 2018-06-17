import pylast
import csv
import configparser

config = configparser.ConfigParser('../../config.ini')

def getSubscriberFromUsers(network, subscribers_tmp):

    subscribers = []

    while(len(subscribers_tmp) != 0):

        # RECUPERATION DES SUBSCRIBERS DES UTILISATEURS A PARCOURIR
        for subscriber in subscribers_tmp:
            user = network.get_user(subscriber)
            print("\n#### Searching subscriber for user : " + str(subscriber) + "  ####")
            user_Subscribers = user.get_friends()

            # RECUPERATION DES SUBSCRIBERS DE CHAQUE SUBSCRIBER DE L'UTILISATEUR INITIAL ET AJOUT DE CES SUBSCRIBERS
            # A LA LISTE DES UTILISATEURS A PARCOURIR
            for user_Subscriber in user_Subscribers:
                if user_Subscriber in subscribers:
                    print("\nUser " + str(user_Subscriber) + " already in list")
                else:
                    subscribers_tmp.append(user_Subscriber)
                    subscribers.append(user_Subscriber)
                    print("\nAdding " + str(user_Subscriber) + " to user list")

                    # RECUPERATION DES 50 DERNIERES MUSIQUES ECOUTEES PAR L'UTILISATEUR
                    listenHistory = getUserTrackList(user_Subscriber)

                    #CREATION DU FICHIER DE DONNEES
                    createDataFiles(user_Subscriber, listenHistory)

            subscribers_tmp.remove(subscriber)

            print("\nUser list length : ", len(subscribers_tmp))


def getUserTrackList(user_subscriber):
    listenHistory = []

    listenHistory_tmp = user_subscriber.get_recent_tracks(limit=50)
    loved_list = user_subscriber.get_loved_tracks()

    # RECUPERATION DES 50 DERNIERES MUSIQUES ECOUTEES PAR L'UTILISATEUR
    for track_tmp in listenHistory_tmp:
        track = track_tmp.track
        title = track.title
        artist = track.artist

        if len(loved_list) == 0:
            loved = 0
        elif track in loved_list:
            loved = 1
        else:
            loved = 0

        listenHistory.append((str(title),str(artist),loved))

    return listenHistory


def createDataFiles(user_subscriber, listenHistory):
    trackList_tmp = []

    # CREATION DU FICHIER DE DONNEES
    with open('subscriber.csv', 'a', newline='', encoding='utf-8') as file:
        userSubscriber = csv.writer(file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)

        for title, artist, loved in listenHistory:
            userSubscriber.writerow([str(user_subscriber)] + [artist] + [title] + [loved])

    # CREATION DE LA LISTE DES TITRES ECOUTES
    with open('trackList.csv', 'a', newline='',encoding='utf-8') as track_List:
        trackList = csv.writer(track_List, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)

        for title, artist, loved in listenHistory:
            track = title + artist

            if  track in trackList_tmp:
                print('track ' + track + ' already in list')
            else :
                print('adding track ' + track + ' in track list')
                trackList.writerow([artist] + [title])
                trackList_tmp.append(track)


def main(network):

    # INITIALISATION DES FICHIERS DE DONNEES
    with open('subscriber.csv', 'w', newline='', encoding='utf-8') as file:
        subscribercsv = csv.writer(file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        subscribercsv.writerow(["User"]+["Artist"]+["Title"]+["Loved"])

    with open('trackList.csv', 'w', newline='', encoding='utf-8') as track_List:
        trackList = csv.writer(track_List, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        trackList.writerow(["Artist"] + ["Title"])

    # DEFINITION DE L'UTILISATEUR INITIAL
    test_user = "casillicaio"
    first_user = network.get_user(test_user)
    print("Start User : " + str(test_user))

    subscribers_tmp = first_user.get_friends()

    getSubscriberFromUsers(network, subscribers_tmp)


if __name__ == '__main__':

    # INITIALISATION DE LA CONNEXION
    lastfm_config = config['LASTFM']
    API_KEY = lastfm_config.lastfm_api_key
    API_SECRET = ""
    username = ""
    password_hash = pylast.md5("")

    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)

    main(network)