from common.serializer import *
from datetime import date


class MypageUserInfSerializer(UserInfSerializer):
    
    class Meta(UserInfSerializer.Meta):
        model = CustomUser
        fields = (*UserInfSerializer.Meta.fields ,"user_profile","birthday")

class ChangeUserInfWriteSerializer(serializers.ModelSerializer):
    
    nickname = serializers.CharField(
        write_only = True,
        allow_null = True,
        required = False,
    )
    
    birthday = serializers.DateField(
        write_only = True,
        allow_null = True,
        required = False,
    )
    icon = serializers.ImageField(
        write_only = True,
        allow_null = True,
        required = False,
    )
    profile_text = serializers.CharField(
        write_only=True,
        allow_null=True,
        required=False,
        allow_blank=True,
    )
    
    class Meta:
        model = CustomUser
        fields = ["nickname", "birthday", "icon","profile_text"]
    
    def validate_nickname(self, nickname :str):
        
        if nickname is None :
            return None
        
        return nickname.strip()
    
    def validate_birthday(self, birthday):
        
        if birthday is None:
            return None
        
        today = date.today()
        
        if birthday > today :
            raise serializers.ValidationError("日付が不正です")
        
        return birthday

    def validate_profile_text(self,profile_text):
        if profile_text is None:
            return None
        
        max_length = 200
        
        if len(profile_text) > max_length :
            raise serializers.ValidationError("文字数は２００までです")
        
        return profile_text
    
    def update(self, instance :CustomUser, validated_data):
        
        #null、つまり指定しないなら更新しない
        if "nickname" in validated_data:
            nickname = validated_data["nickname"]
            if nickname not in ("", None):
                instance.nickname = nickname
            
        if "birthday" in validated_data:
            birthday = validated_data["birthday"]
            if birthday is not None:
                instance.birthday = birthday
        
        if "icon" in validated_data:
            icon = validated_data["icon"]
            if icon is not None:
                instance.user_icon = icon
        
        if "profile_text" in validated_data:
            user_profile = validated_data["profile_text"]
            if user_profile is not None:
                instance.user_profile = user_profile

        instance.save()
        
        return instance

class DetailUserInfReadSerializer(DetailUserInfSerializer):
    date_joined = serializers.SerializerMethodField()
    
    class Meta(DetailUserInfSerializer.Meta):
        
        fields = ["username", "email", "date_joined"]
        
    def get_date_joined(self, obj):
        return obj.date_joined.date().isoformat()

class LayoutReadSerializer(MiniUserInfSerializer):
    
    class Meta(MiniUserInfSerializer.Meta):
        pass

