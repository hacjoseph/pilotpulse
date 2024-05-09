import base64
from django.shortcuts import HttpResponse, redirect
from django.http import HttpRequest 
from django.conf import settings 
import requests
import pkce
from django.utils import timezone
from datetime import timedelta
from fitbit.models import FitbitUser
from pilotes.models import Pilote
import secrets
import logging
from rest_framework.response import Response
from django.core.cache import cache

def authorize_fitbit(request:HttpRequest, pilote_id=None):
    """Cette metode permet de recuperer le code d'authorisation de fitbit pour ce connecter au copmte 
    fitbit d'un pilote

    Args:
        request (HttpRequest): Requette POST http
        pilote_id (int, optional): Identifiant du pilote. Defaults to None.

    Returns:
        Retourne l'url de redirection vers le site de fitbit pour obtenir le code d'authorisation
    """
    if request.method == 'POST':
        if pilote_id is None:
            pilote_id = request.POST.get('pilote_id')
            
        redirect_to = request.data['redirect_to']
        print(redirect_to)
        
        code_verifier, code_challenge = pkce.generate_pkce_pair()
        authorization_url = 'https://www.fitbit.com/oauth2/authorize'
        redirect_uri = 'http://127.0.0.1:8000/fitbit/callback/'
        scopes = 'heartrate' 
        
        # Generation d'un state unique pour assurer la connexion entre notre applicaion et le site de fitbit
        state = secrets.token_urlsafe(16)
        cache_key = f"fitbit_data_{request.session.session_key}"
        data = {
            'code_verifier': code_verifier,
            'state': state,
            'pilote_id': pilote_id,
            'redirect_to': redirect_to
        }
        cache.set(cache_key, data, timeout=None)

        # Constitution de l'url de redirection vers le site de fitbit
        authorization_url += f'?response_type=code&client_id=23RT7L&scope={scopes}&code_challenge={code_challenge}&code_challenge_method=S256&state={state}&redirect_uri={redirect_uri}&pilote_id={pilote_id}&prompt=login'

        response_data = {
            'authorization_url':authorization_url
        }
        return Response(response_data)
    else:
        return HttpResponse("Method not allowed")

def fitbit_callback(request):
    """Cette methode permet de recuperer le accees token, le refresh token et la date d'expirarion du token

    Args:
        request (httpRequest): requte http

    Returns:
        Elle permet de sauvegarder les donnees recuperees dans la base de donnees
    """

    # Recuperation du state et du code d'athorisation de fitbit
    code = request.GET.get('code')
    state = request.GET.get('state')
    cache_key = f"fitbit_data_{request.session.session_key}"
    data = cache.get(cache_key)
    if data:
        code_verifier = data['code_verifier']
        expected = data['state']
        pilote_id = data['pilote_id']
        redirect_to = data['redirect_to']
        cache.delete(cache_key)
        
    logging.debug(f"Authorization code: {code}, State: {state}")

    # Validation du parametre state pour prevenir les attaques CSRF
    if state != expected:
        logging.error("Parametre state invalide")
        return HttpResponse(expected)

    # Constitution de l'url pour la demande de l'access token et le refresh token
    token_endpoint = 'https://api.fitbit.com/oauth2/token'
    payload = {
        # code de l'application creer sur le site de fitbit
        'client_id': settings.FITBIT_CLIENT_ID,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://127.0.0.1:8000/fitbit/callback/',  # Update with your actual redirect URL
        'code': code,
        'code_verifier': code_verifier
    }
    client_id = settings.FITBIT_CLIENT_ID
    client_secret = settings.FITBIT_CLIENT_SECRET
    credentials = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {credentials}'
    }

    # Requete post pour echanger le code d'authorisation par un access token
    response = requests.post(token_endpoint, data=payload, headers=headers)
    token_data = response.json()

    logging.debug(f"Token endpoint response: {token_data}")

    # Verifier si les tokens sont bien recupures
    if 'access_token' in token_data and 'refresh_token' in token_data:
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']
        expires_in = token_data['expires_in']
        
        # Verifier si le compte fitibit existe deja dans la base de donnees
        try:
            fitbit_user = FitbitUser.objects.get(user_id=token_data['user_id'])
        except FitbitUser.DoesNotExist:
            # Creer un nouveau compte fitbit s'il n'exist pas
            fitbit_user = FitbitUser.objects.create(
                user_id=token_data['user_id'],
                access_token=access_token,
                refresh_token=refresh_token,
                token_expiry=timezone.now() + timedelta(seconds=expires_in)
            )
            fitbit_user.save()
            
        associeted = fitbit_user.pilotes
        if fitbit_user.pilotes.exists():
            return HttpResponse("Ce compte Fitbit est déjà associé à un autre pilote.")
        else:
            # Associer les token a un pilote et sauvegarder dans la base de donnees
            pilot = Pilote.objects.get(pk=pilote_id)
            pilot.fitbit_user = fitbit_user
            pilot.save()
        if redirect_to:
            return redirect(redirect_to)
        else:
            return Response("Pas de url de rediection")
    else:
        logging.error("Echec de recuperation des tokens.")
        return HttpResponse("Echec de recuperation des tokens.")

def refresh_access_token(refresh_token):
    """Cette methode permet d'obtenir un nouveau token

    Args:
        refresh_token : le refresh token qui permet d'otenir un nouveau token

    Returns:
        Retourne une reponse de fitbit les nouveaux tokens
    """
    token_endpoint = 'https://api.fitbit.com/oauth2/token'
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': '23RT7L',
        'client_secret': 'd88357cf42ba70d81d9514e4e3aa9a42'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_endpoint, data=payload, headers=headers)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data
    else:
        logging.error(f"Echec lors de la generation d'un nouveau token. Status code: {response.status_code}")

def check_and_refresh_token(pilot):
    """Cette methode permet de verifier si le token est expirer pour demander un nouveau.

    Args:
        pilot : Identifiant du pilote
    """
    if pilot.fitbit_user is None:
        return None
    
    if pilot.fitbit_user.token_expiry <= timezone.now():
        new_access_token = refresh_access_token(pilot.fitbit_user.refresh_token)
        
        if new_access_token is None or 'access_token' not in new_access_token:
            logging.error("Erreur lors de l'obtention du token d'accès.")
            return None
        pilot.fitbit_user.access_token = new_access_token['access_token']
        # pilot.fitbit_user.refresh_token = new_access_token['refresh_token']
        pilot.fitbit_user.token_expiry = timezone.now() + timedelta(seconds=new_access_token['expires_in'])
        pilot.fitbit_user.save()

def retrieve_heart_rate_data(request, experimentation, pilote):
    """Cette methode permet de recuperer les donnees de frequence cardiaque

    Args:
        request (_type_): Requette GET http
        experimentation (_type_): l'identifiant de l'eperimentaion
        pilote (_type_): 'L'identifiant du pilote'

    Returns:
        Retourne les donnees de frequence cardiaque d'un pilote
    """
    fitbit_user = pilote.fitbit_user
    
    if not fitbit_user:
        return HttpResponse("Fitbit user not associated with the pilot.")

    # Veirifier et demander un nouveau token si necessaire
    check_and_refresh_token(pilote)
    
    # Recuperer le token du pilote
    access_token = fitbit_user.access_token
    
    # Constitution de l'url de recuperation des deonnees de frequence cardiaque
    user_id = fitbit_user.user_id 
    start_date = experimentation.date
    end_date = experimentation.date
    start_time = experimentation.temps_debut.strftime("%H:%M")
    end_time = experimentation.temps_fin.strftime("%H:%M")
    detail_level = experimentation.detail_level  

    heart_rate_endpoint = f'https://api.fitbit.com/1/user/{user_id}/activities/heart/date/{start_date}/{end_date}/{detail_level}/time/{start_time}/{end_time}.json'

    headers = {'Authorization': f'Bearer {access_token}'}

    # Requete GET pour recuperer les donnees
    response = requests.get(heart_rate_endpoint, headers=headers)
    
    # Convertion des donnees en json
    heart_rate_data = response.json()
    return heart_rate_data
