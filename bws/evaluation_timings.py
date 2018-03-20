from rest_framework.views import APIView
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.renderers import JSONRenderer
from bws.throttles import BurstRateThrottle, EndUserIDRateThrottle,\
    SustainedRateThrottle
from rest_framework import serializers, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication,\
    SessionAuthentication, TokenAuthentication
from django.conf import settings
import os
import errno
import json
import time


class EvaluationInputSerializer(serializers.Serializer):
    ''' Evaluation timings for events '''
    prototype = serializers.ListField()
    events = serializers.ListField()
    mouse = serializers.ListField()
    # evaluation = serializers.JSONField()


class CanRiskPermission(permissions.BasePermission):
    message = 'Cancer risk factor permission not granted'

    def has_permission(self, request, view):
        return request.user.has_perm('boadicea_auth.can_risk')


class EvaluationView(APIView):
    renderer_classes = (XMLRenderer, JSONRenderer, )
    serializer_class = EvaluationInputSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication, )
    permission_classes = (IsAuthenticated, CanRiskPermission)
    throttle_classes = (BurstRateThrottle, SustainedRateThrottle, EndUserIDRateThrottle)

    def post(self, request):
        """
        Evaluation timings posted and saved in user directory.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            user_dir = os.path.join(settings.CWD_DIR, str(request.user))
            if not os.path.exists(user_dir):
                try:
                    os.makedirs(user_dir)
                    print(user_dir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise

            filepath = os.path.join(user_dir, "eval_" + time.strftime("%Y%m%d-%H%M%S"))
            f = open(filepath, "w")
            print(json.dumps(validated_data), file=f)

            return Response()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)