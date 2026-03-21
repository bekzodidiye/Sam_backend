from modeltranslation.translator import register, TranslationOptions
from .models.core import Rule, Message
from .models.sales import Tariff, SalesLink

@register(Rule)
class RuleTranslationOptions(TranslationOptions):
    fields = ('content',)

@register(Message)
class MessageTranslationOptions(TranslationOptions):
    fields = ('text',)

@register(Tariff)
class TariffTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(SalesLink)
class SalesLinkTranslationOptions(TranslationOptions):
    fields = ('name',)
