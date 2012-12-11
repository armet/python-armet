from .base import BaseTest
from armet.utils import test
from armet import http
from .models import Choice, Poll
from datetime import datetime
from dateutil.parser import parse


class GetBase(object):
    """Common test cases for GET operations."""

    formats = ('json', 'xml')

    def test_list(self):
        """Asserts the list view returns valid content."""
        for format in self.formats:
            url = '{}{}.{}'.format(self.endpoint, self.model, format)
            response = self.client.get(url)
            self.deserialize(response, format)
            self.assertHttpStatus(response, http.client.OK)

    def test_get_id(self):
        """Gets choice id"""
        for format in self.formats:
            url = '{}{}/1/id.{}'.format(self.endpoint, self.model, format)
            response = self.client.get(url)
            self.deserialize(response, format)
            self.assertHttpStatus(response, http.client.OK)

    def test_get_uri(self):
        """Gets poll uri"""
        for format in self.formats:
            url = '{}{}/1/resource_uri.{}'.format(self.endpoint,
                self.model, format)
            response = self.client.get(url)

            self.deserialize(response, format)
            self.assertHttpStatus(response, http.client.OK)


class ChoiceTest(GetBase, BaseTest, test.TestCase):

    endpoint = '/'
    model = 'choice'

    def setUp(self):
        super(ChoiceTest, self).setUp()

    def test_get_choice_votes(self):
        """Gets choice votes"""
        response = self.client.get(self.endpoint + 'choice/1/votes.{}/'
            .format('xml'))
        self.assertHttpOK(response)
        self.assertValidXML(response)
        response = self.client.get(self.endpoint + 'choice/1/votes.{}/'
            .format('json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_choicetext(self):
        """Gets choice text"""
        response = self.client.get(self.endpoint + 'choice/1/choice_text.{}/'
            .format('xml'))
        self.assertHttpOK(response)
        self.assertValidXML(response)
        response = self.client.get(self.endpoint + 'choice/1/choice_text.{}/'
            .format('json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)


class PollTest(GetBase, BaseTest, test.TestCase):

    endpoint = '/'
    model = 'poll'

    def setUp(self):
        super(PollTest, self).setUp()
        self.poll = Poll.objects.create(
            question="Why???How????When????",
            pub_date='1988-10-08T10:11:12+01:00'
        )
        self.choice_one = Choice.objects.create(
            poll=self.poll,
            choice_text="Because...",
            votes=5
        )

    def test_get_poll_question(self):
        """Gets poll question"""
        response = self.client.get(self.endpoint + 'poll/1/question.{}/'
            .format('json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        response = self.client.get(self.endpoint + 'poll/1/question.{}/'
            .format('xml'))
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_poll_pubdate_xml(self):
        """Gets poll publication date"""
        response = self.client.get(self.endpoint + 'poll/1/pub_date.{}/'
            .format('json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        response = self.client.get(self.endpoint + 'poll/1/pub_date.{}/'
            .format('xml'))
        self.assertHttpOK(response)
        self.assertValidXML(response)

    # def test_recursiveness(self):
    #     url = 'poll/{}/'.format(self.poll.id)
    #     for x in range(0, 10):
    #         url += 'choices/{}/poll/'.format(self.choice_one.id)
    #     url += 'choices'
    #     response = self.client.get(self.endpoint + url)
    #     print(url)
    #     self.assertHttpOK(response)
    #     self.assertValidXML(response)

    def test_get_question(self):
        response = self.client.get(self.endpoint + 'poll/{}/question.{}/'
            .format(self.poll.id, 'xml'))
        self.assertHttpOK(response)
        self.assertValidXML(response)
        response = self.client.get(self.endpoint + 'poll/{}/question.{}/'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_question_string_array(self):
        for x in range(1, (len(self.poll.question))):
            response = self.client.get(self.endpoint + 'poll/{}/question/{}.{}'
                .format(self.poll.id, x, 'json'))

            self.assertHttpOK(response)
            self.assertValidJSON(response)
            content = self.deserialize(response, format='json')
            self.assertEqual(self.poll.question[x-1], content[0])

    def test_question_length(self):
        response = self.client.get(self.endpoint + 'poll/{}/question/length.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        self.assertEqual(len(self.poll.question), content[0])

    def test_get_year_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/year.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        self.assertEqual(t.year, content[0])

    def test_get_month_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/month.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        self.assertEqual(t.month, content[0])

    def test_get_day_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/day.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        self.assertEqual(t.day, content[0])

    def test_get_weekday_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/weekday.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        self.assertEqual(t.isoweekday(), content[0])

    def test_get_yearday_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/yearday.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        self.assertEqual(t.timetuple().tm_yday, content[0])

    def test_get_hour_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/hour.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        self.assertEqual(t.hour, content[0])

    def test_get_minute_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/minute.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        self.assertEqual(t.minute, content[0])

    def test_get_second_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/second.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        self.assertEqual(t.second, content[0])

    def test_get_millisecond_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/millisecond.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        self.assertEqual(t.microsecond / 1000.0, content[0])

    def test_get_microsecond_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/microsecond.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        self.assertEqual(t.microsecond, content[0])

    # def test_get_dst_on_pubdate(self):
    #     response = self.client.get(self.endpoint + 'poll/{}/pub_date/dst.{}'
    #         .format(self.poll.id, 'json'))
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, format='json')
    #     t = parse(self.poll.pub_date)
    #     dst = t.dst() if t.dst() is not None else datetime.timedelta()
    #     self.assertEqual(dst, content[0])

    def test_get_tzname_on_pubdate(self):
        response = self.client.get(self.endpoint + 'poll/{}/pub_date/timezone.{}'
            .format(self.poll.id, 'json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, format='json')
        t = parse(self.poll.pub_date)
        print(t.tzname())
        self.assertEqual(t.tzname(), content[0])

