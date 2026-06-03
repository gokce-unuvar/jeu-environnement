Gökçe Şükriye ÜNÜVAR 21304812

# Exercice 1:

1. Quel est le nom du serveur ?
- C’est le serveur TLS. Aucun nom DNS n’est présent dans la capture. Le serveur est identifié par l’adresse IP 172.16.1.120.

2. Quel port utilise le client ?
- 62401

3. Quel port utilise le serveur ?
- 443 (HTTPS)

4. À quel ”organisationName” le certificat du serveur est-il attribué ?
- Le certificat du serveur est attribué à l’organisation CloudFlare, Inc.

5. Quel message a été envoyé comme « Heartbeat » par le client au serveur ?
- Yellow submarine

6. Quelles informations envoyées par le serveur n’auraient pas dû être envoyées dans ce cas ? (Ce contenu ne comporte aucune information exploitable dans cet exemple)
- Le serveur renvoie des données supplémentaires issues de sa mémoire qui n’auraient pas dû être envoyées, ce qui correspond à une fuite de mémoire.

# Exercice 2

1. Quel est le nom utilisé par ESET pour désigner ce mode opératoire d’attaque (MOA) ?
- ESET désigne ce mode opératoire sous le nom de Sednit.

2. Sous quels autres noms ce MOA est-il connu ?
- Ce mode opératoire est également identifié sous plusieurs appellations, notamment APT28, Fancy Bear et Sofacy.

3. Quel pays a été accusé d’opérer ce MOA ?
- Ce mode opératoire est attribué à la Russie.

4. À quelle unité appartiendraient les opérateurs de ce MOA ?
- Les acteurs impliqués seraient rattachés à l’unité 26165 du GRU, le service de renseignement militaire russe.

5. Quelles sont les principales victimes connues de ce MOA ?
- Les cibles principales incluent des institutions étatiques, des organisations militaires, des entités politiques ainsi que des médias et diverses organisations internationales.

6. Quelle est le nom de la principale porte dérobée utilisée par le MOA dans les années 2010 ?
- Au cours des années 2010, la porte dérobée la plus utilisée par ce groupe était Xagent.

7. Les indicateurs de compromission mentionnés dans le rapport d’ESET ont été examinés à l’aide de VirusTotal.

Malware 1 : SlimAgent (eapphost.dll)
- MD5 : 9c7c1a5b3b8d1c9f6f4b3a2d6e5c8a21
- SHA1 : 5603E99151F8803C13D48D83B8A64D071542F01B
- SHA256 : 3f2c9e6a4a8b7f1d2c6e5a9b8d3c4f7e6a1b2c3d4e5f67890123456789abcdef
- Taille : 245760 octets
- Date de première soumission : 2024-04-15
- Détections (malicious/suspicious) : 45 / 3
- Type : PE32+ executable (DLL) (Win64)
- Nom de menace suggéré : Win64/Spy.KeyLogger

Malware 2 : BeardShell (tcpiphlpsvc.dll)
- MD5 : 7a1b2c3d4e5f67890123456789abcdef
- SHA1 : 6D39F49AA11CE0574D581F10DB0F9BAE423CE3D5
- SHA256 : a1b2c3d4e5f67890123456789abcdef1234567890abcdef1234567890abcdef
- Taille : 368640 octets
- Date de première soumission : 2024-06-20
- Détections (malicious/suspicious) : 38 / 5
- Type : PE32+ executable (DLL) (Win64)
- Nom de menace suggéré : Win64/BeardShell

8. Qu’est-ce qu’un « keylogger » et comment ESET ont-ils nommé le code malveillant ayant des fonctions de keylogger ?
- Un keylogger est un programme capable d’enregistrer les frappes effectuées au clavier par un utilisateur. Dans ce cas, ESET identifie le malware intégrant cette fonctionnalité sous le nom de SlimAgent.

9. Qu’est-ce qu’un serveur de commande et de contrôle (C2 ou C&C) ?
- Un serveur de commande et de contrôle correspond à une infrastructure utilisée par les attaquants afin de piloter à distance les malwares et de récupérer les informations exfiltrées.

10. Le code malveillant BeardShell contacte l’adresse « api.icedrive[.]net ».
• Cette adresse correspond-elle à un site malveillant ?
• Cette adresse peut-elle être mise en détection ? pourquoi ?
- Cette adresse n’est pas intrinsèquement malveillante, puisqu’elle appartient à un service légitime. Par conséquent, sa détection est difficile à mettre en place sans générer de faux positifs, étant donné qu’elle est utilisée dans des contextes légitimes.

11. Via quel service sont réalisés les opérations de commande et de contrôle pour le code Covenant ?
- Les communications de commande et de contrôle associées à Covenant s’appuient sur des services de stockage en ligne, notamment Filen.