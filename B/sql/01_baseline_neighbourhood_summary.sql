
with calendar_30 as (
    select
        listing_id,
        avg(price) as avg_calendar_price_30,
        avg(case when available then 1.0 else 0.0 end) as availability_30_rate
    from core.calendar_day
    where date >= (select max(date) - interval '30 days' from core.calendar_day)
    group by listing_id
),
review_counts as (
    select
        listing_id,
        count(*) as total_reviews
    from core.review
    group by listing_id
)
select
    n.name as neighbourhood,
    count(l.listing_id) as num_listings,
    round(avg(l.listing_price), 2) as avg_price,
    percentile_cont(0.5) within group (order by l.listing_price) as median_price,
    round(avg(l.minimum_nights), 2) as avg_minimum_nights,
    coalesce(sum(r.total_reviews), 0) as total_reviews,
    round(coalesce(sum(r.total_reviews), 0)::numeric / count(l.listing_id), 2)
        as reviews_per_listing,
    round(avg(coalesce(c.availability_30_rate, 0)), 4) as availability_30_rate
from core.listing l
inner join core.neighbourhood n on l.neighbourhood_id = n.neighbourhood_id
left join calendar_30 c on l.listing_id = c.listing_id
left join review_counts r on l.listing_id = r.listing_id
group by n.name
order by num_listings desc
