import {
  CalendarDays,
  Layers,
  Mail,
  Megaphone,
  Rocket,
  Search,
  Swords,
  Users,
} from 'lucide-react'

/**
 * Ready-to-render result card presets for the eight core AI outputs.
 * Pass these to <ResultCards results={...} /> or map over them directly.
 */
export const RESULT_PRESETS = [
  {
    id: 'marketing-strategy',
    title: 'Marketing Strategy',
    description:
      'A complete go-to-market plan built around your goals, audience, and budget.',
    icon: Rocket,
    tone: 'indigo',
    items: ['Positioning & messaging', 'Channel mix recommendation', '90-day roadmap'],
    content: [
      {
        heading: 'Positioning',
        points: [
          'Lead with the outcome: faster growth without the guesswork.',
          'Differentiate on AI-personalized strategy, not generic templates.',
        ],
      },
      {
        heading: 'Channels',
        points: [
          'Email: nurture high-intent leads from day one.',
          'Paid social: retarget engaged visitors within 7 days.',
        ],
      },
    ],
  },
  {
    id: 'customer-persona',
    title: 'Customer Persona',
    description:
      'A data-informed snapshot of your ideal buyer and what drives their decisions.',
    icon: Users,
    tone: 'purple',
    items: ['Demographics & goals', 'Pain points', 'Buying triggers'],
    content: [
      {
        heading: 'Demographics',
        points: [
          '30-45 year old decision-makers at SMBs.',
          'Comfortable with SaaS tools and automation.',
        ],
      },
      {
        heading: 'Pain points',
        points: [
          'Wasting time on trial-and-error marketing.',
          'No clear view of what their competitors are doing.',
        ],
      },
    ],
  },
  {
    id: 'seo',
    title: 'SEO Ideas',
    description:
      'High-intent topics and keywords to close your visibility gaps.',
    icon: Search,
    tone: 'cyan',
    items: ['12 keyword gaps found', '5 quick-win content topics'],
    content: [
      {
        heading: 'Quick wins',
        points: [
          '“AI marketing strategy for small teams” — low competition.',
          '“Competitor analysis tools compared” — high commercial intent.',
        ],
      },
      {
        heading: 'Content plan',
        points: [
          'Publish 2 pillar posts and 3 supporting articles per month.',
          'Add internal links from high-traffic pages to new posts.',
        ],
      },
    ],
  },
  {
    id: 'content-calendar',
    title: 'Content Calendar',
    description:
      'Four weeks of ready-to-publish content aligned to your goals.',
    icon: CalendarDays,
    tone: 'rose',
    items: ['3 blog posts', '2 email campaigns', 'Weekly social cadence'],
    content: [
      {
        heading: 'Week 1',
        points: [
          'Blog: “Why most marketing plans fail” + launch email.',
          'Social: 3 educational posts, 1 behind-the-scenes.',
        ],
      },
      {
        heading: 'Week 2-4',
        points: [
          'Case study spotlight and product-led deep dive.',
          'Retargeting sequence to engaged subscribers.',
        ],
      },
    ],
  },
  {
    id: 'email-campaign',
    title: 'Email Campaign',
    description:
      'High-converting sequence drafts with subject lines that get opened.',
    icon: Mail,
    tone: 'amber',
    items: ['5-email nurture sequence', 'Subject line variants', 'CTA strategy'],
    content: [
      {
        heading: 'Sequence',
        points: [
          'Email 1: Problem story + value promise.',
          'Email 3: Social proof with a mini case study.',
          'Email 5: Deadline-driven offer with clear CTA.',
        ],
      },
      {
        heading: 'Subject lines',
        points: [
          '“The 4-hour marketing plan” (curiosity).',
          '“Your competitors already read this” (relevance).',
        ],
      },
    ],
  },
  {
    id: 'ad-ideas',
    title: 'Advertisement Ideas',
    description:
      'Platform-specific ad concepts with hooks and targeting suggestions.',
    icon: Megaphone,
    tone: 'emerald',
    items: ['3 paid social concepts', 'Search ad copy', 'Audience targeting'],
    content: [
      {
        heading: 'Paid social',
        points: [
          'Video: 15s “before/after” of strategy generation.',
          'Carousel: “5 marketing mistakes you can skip”.',
        ],
      },
      {
        heading: 'Search ads',
        points: [
          'Headline: “AI Marketing Strategist” + offer extension.',
          'Target: “marketing automation”, “competitor analysis”.',
        ],
      },
    ],
  },
  {
    id: 'swot-analysis',
    title: 'SWOT Analysis',
    description:
      'A structured look at your strengths, weaknesses, opportunities, and threats.',
    icon: Layers,
    tone: 'blue',
    items: ['Strengths & weaknesses', 'Opportunities', 'Threats'],
    content: [
      {
        heading: 'Strengths',
        points: ['Fast time-to-value with AI-generated drafts.', 'Adaptable across industries.'],
      },
      {
        heading: 'Threats',
        points: ['Free DIY templates competing on price.', 'AI fatigue in marketing teams.'],
      },
    ],
  },
  {
    id: 'competitor-analysis',
    title: 'Competitor Analysis',
    description:
      'How your rivals position, price, and market — and where you can win.',
    icon: Swords,
    tone: 'fuchsia',
    items: ['Top 3 competitors mapped', 'Pricing & positioning', 'Gap opportunities'],
    content: [
      {
        heading: 'Positioning',
        points: [
          'Competitor A: enterprise-focused, expensive.',
          'Competitor B: template-driven, low price.',
        ],
      },
      {
        heading: 'Your edge',
        points: [
          'Own the mid-market with personalized AI strategy.',
          'Undercut on time-to-value, not price.',
        ],
      },
    ],
  },
]

export default RESULT_PRESETS
