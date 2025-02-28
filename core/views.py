from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from .models import Cattle

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Cattle  # Make sure to import the Cattle model

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # This ensures only authenticated users can access the view
def create_cattle(request):
    """
    Create a new cattle.
    """

    breed = request.data.get('breed')
    birth_date = request.data.get('birth_date')
    ear_tag_no = request.data.get('ear_tag_no')
    dam_id = request.data.get('dam_id')
    sire_id = request.data.get('sire_id')
    picture = request.data.get('picture')
    health_status = request.data.get('health_status')
    gender = request.data.get('gender')
    
    # Check if the input consists of the necessary fields i.e (ear_tag_no, gender)
    if not ear_tag_no or not gender:
        return Response({'error': 'At least Ear_tag_number and gender are required to register cattle!'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the cattle with this ear tag number already exists
    if Cattle.objects.filter(ear_tag_no=ear_tag_no).exists():
        return Response({'error': 'Cattle with this ear tag number already exists!'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create a new cattle object
    new_cattle = Cattle.objects.create(
        breed=breed,
        birth_date=birth_date,
        ear_tag_no=ear_tag_no,
        dam_id=dam_id,
        sire_id=sire_id,
        picture=picture,
        health_status=health_status,
        gender=gender,  # Ensure to include gender
    )
    
    # Save the cattle object
    new_cattle.save()
    
    return Response({
        'id': new_cattle.id,
        'ear_tag_no': new_cattle.ear_tag_no,
        'breed': new_cattle.breed,
        'birth_date': new_cattle.birth_date.strftime('%Y-%m-%d'),
        'dam_id': new_cattle.dam_id,
        'sire_id': new_cattle.sire_id,
        'picture': new_cattle.picture.url,
        'health_status': new_cattle.health_status,
        'gender': new_cattle.gender,
        'created_at': new_cattle.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    }, status=status.HTTP_201_CREATED)

    
#api view to get all cattle
@api_view(['GET'])
def get_all_cattle(request):
    """
    Get all cattle.
    """
    cattle = Cattle.objects.all()
    response = []
    for c in cattle:
        response.append({
            'id': c.id,
            'ear_tag_no': c.ear_tag_no,
            'breed': c.breed,
            'birth_date': c.birth_date.strftime('%Y-%m-%d'),
            'dam_id': c.dam_id,
            'sire_id': c.sire_id,
            'picture': c.picture.url,
            'health_status': c.health_status,})
    return Response(response, status=status.HTTP_200_OK)

#api view to get cattle by id
@api_view(['GET'])

def get_cattle_by_id(request, cattle_id):
    """
    Get a cattle by its id.
    """
    try:
        cattle = Cattle.objects.get(id=cattle_id)
        return Response({
            'id': cattle.id,
            'ear_tag_no': cattle.ear_tag_no,
            'breed': cattle.breed,
            'birth_date': cattle.birth_date.strftime('%Y-%m-%d'),
            'dam_id': cattle.dam_id,
            'sire_id': cattle.sire_id,
            'picture': cattle.picture.url,
            'health_status': cattle.health_status,})
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found!'}, status=status.HTTP_404_NOT_FOUND)
    
#api view to update cattle by id

@api_view(['PUT'])
@permission_classes([IsAuthenticated])  # This ensures only authenticated users can access the view
def update_cattle_by_id(request, cattle_id):
    """
    Update a cattle by its id.
    """
    try:
        cattle = Cattle.objects.get(id=cattle_id)
        cattle.breed = request.data.get('breed', cattle.breed)
        cattle.birth_date = request.data.get('birth_date', cattle.birth_date)
        cattle.ear_tag_no = request.data.get('ear_tag_no', cattle.ear_tag_no)
        cattle.dam_id = request.data.get('dam_id', cattle.dam_id)
        cattle.sire_id = request.data.get('sire_id', cattle.sire_id)
        cattle.picture = request.data.get('picture', cattle.picture)
        cattle.health_status = request.data.get('health_status', cattle.health_status)
    
        cattle.save()
        return Response({
            'id': cattle.id,
            'ear_tag_no': cattle.ear_tag_no,
            'breed': cattle.breed,
            'birth_date': cattle.birth_date.strftime('%Y-%m-%d'),
            'dam_id': cattle.dam_id,
            'sire_id': cattle.sire_id,
            'picture': cattle.picture.url,
            'health_status': cattle.health_status,})
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found!'}, status=status.HTTP_404_NOT_FOUND)

#api view to delete cattle by id
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])  # This ensures only authenticated users can access the view
def delete_cattle_by_id(request, cattle_id):
    """
    Delete a cattle by its id.
    """
    try:
        cattle = Cattle.objects.get(id=cattle_id)
        cattle.delete()
        return Response({'message': 'Cattle deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    except Cattle.DoesNotExist:
        return Response({'error': 'Cattle not found!'}, status=status.HTTP_404_NOT_FOUND)



