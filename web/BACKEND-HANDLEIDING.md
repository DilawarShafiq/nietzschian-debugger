# GreenPT-backend op een VPS

Deze Express-backend ontvangt oefengesprekken op `POST /api/chat` en roept
GreenPT vanuit Node.js aan. Dat vermijdt browser-CORS bij GreenPT, maar lost een
ongeldige sleutel, ontbrekende modeltoegang of een providerblokkade niet op.
Het is de bestaande reflectie-API, geen algemene OpenAI-proxy.

## 1. Voorbereiden

Gebruik een VPS met Docker Engine en de Compose-plugin, of een compatibele
OCI-runtime. De voorbeelden gebruiken Docker. Installeer die volgens de
officiële handleiding voor jouw Linux-distributie. Je VPS-IP is voldoende voor
SSH; voor de verbinding vanaf HTTPS GitHub Pages heb je ook een HTTPS-backend
nodig, meestal met een domeinnaam en geldig TLS-certificaat.

Gebruik uitsluitend fictieve/geanonimiseerde oefencasussen. De backendoperator
kan de tekst zien; tekst en systeemprompt worden naar GreenPT gestuurd.
Deze app is geen medisch hulpmiddel.

## 2. Code en geheime configuratie

Op de VPS:

```bash
git clone --branch feature/psychology-reflection \
  https://github.com/bartvanderwal/nietzschian-diagnoser.git
cd nietzschian-diagnoser/web
cp .env.example .env
chmod 600 .env
openssl rand -hex 32
```

Open `.env` in een editor. Plak je **nieuwe GreenPT-sleutel** in
`GREENPT_API_KEY` en de uitvoer van `openssl` in `BACKEND_ACCESS_TOKEN`.
Gebruik twee verschillende geheimen:

```dotenv
GREENPT_API_KEY=vervang-door-je-greenpt-sleutel
GREENPT_MODEL=mistral-small-3.2-24b-instruct-2506
BACKEND_ACCESS_TOKEN=vervang-door-het-willekeurige-toegangstoken
FRONTEND_ORIGIN=https://bartvanderwal.github.io
```

Controleer het model voor jouw account; `glm-5.3` is hier niet geverifieerd.
De origin bevat geen pad, dus niet `/nietzschian-diagnoser/`.
De Compose-configuratie stelt `ALLOW_SERVER_KEY=true` in; het proces weigert
dan te starten zonder toegangstoken van minimaal 32 tekens.

Commit `.env` niet. Het Docker-buildcontext sluit alle bestanden uit behalve
expliciet benodigde bronbestanden; `.env` en de repository-`.env` zitten niet
in het image. Runtimegeheimen via environment zijn wel zichtbaar voor beheerders
met Docker/root-toegang. Deel geen `docker inspect`- of `docker compose config`-
uitvoer: die kan geheimen bevatten.

## 3. Bouwen en starten

```bash
docker compose up -d --build
docker compose ps
curl --fail http://127.0.0.1:3080/healthz
```

De laatste opdracht geeft `{"status":"ok"}`. Dat controleert alleen Express,
niet de sleutel of GreenPT-bereikbaarheid. Het image draait als niet-root met
alleen de gebouwde API en productiedependencies. Compose gebruikt een read-only
filesystem, geen Linux-capabilities en `no-new-privileges`.
Poort 3080 is alleen aan VPS-loopback gekoppeld, niet aan het internet.

Bij fouten:

```bash
docker compose logs --tail=50 backend
```

De app logt geen sleutels, prompts of provider-errorbodies. Een aparte
reverse proxy mag eveneens geen requestbodies of Authorization-headers loggen.

## 4. HTTPS op je domein

Laat bijvoorbeeld `greenpt.jouwdomein.nl` via DNS naar je VPS wijzen.
Gebruik je bestaande HTTPS-reverse proxy, of installeer Caddy op de VPS.
Voor Caddy **op de host**:

```caddyfile
greenpt.jouwdomein.nl {
    reverse_proxy 127.0.0.1:3080
}
```

Voeg dit toe aan je bestaande configuratie; overschrijf andere sites niet.
Gebruik de Caddy-instructies om de configuratie te valideren en herladen.
Open poort 80/443 voor certificaatuitgifte/HTTPS en behoud je SSH-toegang.
Exposeer 3080 niet publiek. Caddy in een container heeft een andere
netwerkconfiguratie nodig: `127.0.0.1` verwijst daar naar die container.

```bash
curl --fail https://greenpt.jouwdomein.nl/healthz
```

De backend vertrouwt standaard geen forwarded IP-headers. Achter de proxy is
de limiet van 20 requests per 10 minuten daardoor doorgaans **gedeeld door alle
bezoekers**. Dit is bewust conservatief; zet niet zomaar `trust proxy=true`.
De in-memorylimiet reset bij een restart en is geen harde kostenlimiet.
Stel ook budget/quota's in bij GreenPT.

## 5. GitHub Pages koppelen

In je fork: **Settings → Secrets and variables → Actions → Variables**.
Voeg de repositoryvariabele toe:

```text
CLINICIAN_API_URL=https://greenpt.jouwdomein.nl
```

Dit is een publieke URL, **geen geheim**. Zet geen sleutel of toegangstoken
in die variabele. Draai daarna de workflow
**Clinician demo on GitHub Pages (fork only)** vanaf de featurebranch opnieuw.

In de webapp:

1. Kies **Live model** en **GreenPT**.
2. Kies **Via ingestelde backend** (standaard als de URL geconfigureerd is).
3. Plak het **backend-toegangstoken**, niet de GreenPT-sleutel.
4. Klik **Verbinding valideren** (of druk Enter in het tokenveld). De backend controleert zijn GreenPT-sleutel en het ingestelde model via de modellen-API; dit is geen betaald proefgesprek. De live chat blijft verborgen tot deze controle slaagt.
5. Bevestig dat je een oefencasus gebruikt en verstuur een vraag. Quota of gespreksrechten kunnen alsnog een expliciete fout geven.

Het token blijft alleen in paginageheugen en gaat als bearer-header naar jouw
backend. Browser-JavaScript kan het lezen. Het is een gedeeld demowachtwoord,
geen individuele accountauthenticatie; iedereen met het token kan kosten maken.
De backend gebruikt de server-GreenPT-sleutel. Route/provider wisselen wist
berichten en tijdelijke geheimen na bevestiging. Claude blijft rechtstreeks
werken, en de directe GreenPT-route blijft beschikbaar; er is geen stille fallback.

Lokale frontend met backend:

```bash
VITE_API_BASE_URL=https://greenpt.jouwdomein.nl npm run dev
```

Zet voor lokale toegang `FRONTEND_ORIGIN=http://127.0.0.1:3080` op de backend
en herstart de container. Er wordt één exacte frontend-origin toegestaan.

## 6. Problemen herkennen

- **401 BACKEND_AUTH:** verkeerd/ontbrekend backend-token. Provider wordt niet gebeld.
- **403 FORBIDDEN:** de frontend-origin komt niet overeen met `FRONTEND_ORIGIN`.
- **PROVIDER_AUTH:** GreenPT weigert de sleutel (401).
- **PROVIDER_FORBIDDEN:** GreenPT weigert toegang (403), ook vanuit Node.js.
  Controleer accountrechten/providerbeleid; rapporteer status en tijd aan
  GreenPT-support, nooit de sleutel.
- **PROVIDER_UNAVAILABLE:** netwerk, modeltoegang of geen bruikbare providerresponse.
- **INVALID_RESPONSE:** na één herformulering geen geldig reflectieantwoord.
- **429 RATE_LIMIT:** lokale gedeelde backendlimiet.
- **PROVIDER_RATE_LIMIT:** GreenPT-quota bereikt.
- **Browser fetch-fout:** controleer HTTPS/certificaat, backendbereikbaarheid en origin.
  GreenPT-CORS speelt geen rol bij de Node.js-providercall.

Een geslaagde echte vraag kan geld kosten (maximaal twee modelaanroepen).
Tokenmeters tonen gerapporteerd verbruik; bij fouten kan verbruik onbekend zijn.
Geen echte sleutel is nodig voor unit-tests en container-healthchecks.

## 7. Bijwerken, stoppen en roteren

```bash
git pull --ff-only
docker compose up -d --build
docker compose down
```

Voor sleutel/tokenrotatie: wijzig `.env` in de editor en gebruik
`docker compose up -d --force-recreate`. Een gewone restart leest geen nieuwe
Compose-environment in. Geef het nieuwe backend-token alleen aan toegestane
demogebruikers. Publiceer deze gedeelde backend niet als onbeperkte publieke dienst.

Voor een andere CPU-architectuur kun je een image met Docker Buildx bouwen:

```bash
docker buildx build --platform linux/amd64 --load \
  -t nietzschian-greenpt-backend:local .
```

Kies `linux/arm64` voor een ARM-VPS. De Dockerfile gebruikt standaard
containerinstructies en het image kan met een OCI-compatibele runtime draaien;
de Compose-opdrachten zelf zijn runtimeafhankelijk.
