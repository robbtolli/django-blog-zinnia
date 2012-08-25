"""Views for Zinnia archives"""
import datetime

from django.views.generic.dates import BaseArchiveIndexView
from django.views.generic.dates import BaseYearArchiveView
from django.views.generic.dates import BaseMonthArchiveView
from django.views.generic.dates import BaseWeekArchiveView
from django.views.generic.dates import BaseDayArchiveView
from django.views.generic.dates import BaseTodayArchiveView

from zinnia.settings import HIDE_LOGIN_REQUIRED_ENTRIES
from zinnia.models import Entry
from zinnia.views.mixins.archives import ArchiveMixin
from zinnia.views.mixins.archives import PreviousNextPublishedMixin
from zinnia.views.mixins.callable_queryset import CallableQuerysetMixin
from zinnia.views.mixins.templates import \
     EntryQuerysetArchiveTemplateResponseMixin
from zinnia.views.mixins.templates import \
     EntryQuerysetArchiveTodayTemplateResponseMixin
from zinnia.views.mixins.tz_fixes import EntryDayTZFix
from zinnia.views.mixins.tz_fixes import EntryWeekTZFix
from zinnia.views.mixins.tz_fixes import EntryMonthTZFix


class EntryArchiveMixin(ArchiveMixin,
                        PreviousNextPublishedMixin,
                        CallableQuerysetMixin,
                        EntryQuerysetArchiveTemplateResponseMixin):
    """
    Mixin combinating:

    - ArchiveMixin configuration centralizing conf for archive views
    - PreviousNextPublishedMixin for returning published archives
    - CallableQueryMixin to force the update of the queryset
    - EntryQuerysetArchiveTemplateResponseMixin to provide a
      custom templates for archives
    """
    queryset = Entry.published.all
    
    def get_queryset(self):
        """
        If the user is not logged-in and HIDE_LOGIN_REQUIRED_ENTRIES is set to
        True, return  a queryset foronly the published entries that aren't 
        login_required. Otherwise, return a queryset for all published entries
        """
        if HIDE_LOGIN_REQUIRED_ENTRIES and \
           not self.request.user.is_authenticated():
            return Entry.anon_viewable_published.all
        return super(EntryArchiveMixin,self)


class EntryIndex(EntryArchiveMixin,
                 EntryQuerysetArchiveTodayTemplateResponseMixin,
                 BaseArchiveIndexView):
    """View returning the archive index"""
    context_object_name = 'entry_list'


class EntryYear(EntryArchiveMixin, BaseYearArchiveView):
    """View returning the archive for a year"""
    make_object_list = True
    template_name_suffix = '_archive_year'


class EntryMonth(EntryMonthTZFix, EntryArchiveMixin, BaseMonthArchiveView):
    """View returning the archive for a month"""
    template_name_suffix = '_archive_month'


class EntryWeek(EntryWeekTZFix, EntryArchiveMixin, BaseWeekArchiveView):
    """View returning the archive for a week"""
    template_name_suffix = '_archive_week'

    def get_dated_items(self):
        """Override get_dated_items to add a useful 'week_end_day'
        variable in the extra context of the view"""
        self.date_list, self.object_list, extra_context = super(
            EntryWeek, self).get_dated_items()
        extra_context['week_end_day'] = extra_context[
            'week'] + datetime.timedelta(days=6)
        return self.date_list, self.object_list, extra_context


class EntryDay(EntryDayTZFix, EntryArchiveMixin, BaseDayArchiveView):
    """View returning the archive for a day"""
    template_name_suffix = '_archive_day'


class EntryToday(EntryDayTZFix, EntryArchiveMixin, BaseTodayArchiveView):
    """View returning the archive for the current day"""
    template_name_suffix = '_archive_today'

    def get_dated_items(self):
        """Return (date_list, items, extra_context) for this request.
        And defines self.year/month/day for
        EntryQuerysetArchiveTemplateResponseMixin."""
        today = datetime.date.today()
        self.year, self.month, self.day = today.isoformat().split('-')
        return self._get_dated_items(today)
