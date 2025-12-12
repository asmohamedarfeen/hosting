# Activity Streaks Calendar Feature

## Overview

The Activity Streaks Calendar is a comprehensive feature that allows users to track their daily activities, visualize their progress through an interactive calendar, and build consistent habits. This feature includes a monthly calendar view, streak tracking, activity logging, and detailed statistics.

## Features

### 🗓️ Interactive Calendar
- **Monthly View**: Navigate through months to see activity patterns
- **Visual Indicators**: Green days show completed activities
- **Streak Indicators**: Yellow dots show current streak progress
- **Today Highlighting**: Current day is highlighted with a blue border
- **Responsive Design**: Works on desktop and mobile devices

### 📊 Statistics Dashboard
- **Total Current Streak**: Sum of all current streaks across activity types
- **Longest Streak Ever**: Highest streak achieved in any activity
- **Activity Types**: Number of different activities being tracked
- **Today's Activities**: Count of activities logged today

### 📝 Activity Logging
- **Multiple Activity Types**: Coding, networking, learning, exercise, reading, writing, meditation, planning
- **Optional Descriptions**: Add details about what was accomplished
- **Real-time Updates**: Calendar and stats update immediately after logging
- **Duplicate Prevention**: Can't log the same activity type twice in one day

### 🔥 Streak Management
- **Automatic Calculation**: Streaks are calculated automatically based on consecutive days
- **Streak Reset**: Missing a day resets the streak counter
- **Longest Streak Tracking**: Records the highest streak achieved
- **Visual Progress**: See streak progress in the calendar

## Technical Implementation

### Backend API Endpoints

#### `GET /streaks/page`
- Serves the main streaks page with calendar
- Requires authentication

#### `GET /streaks/demo`
- Serves a demo page with sample data
- No authentication required (for demonstration purposes)

#### `GET /streaks/get-streak-stats`
- Returns overall streak statistics
- Includes total current streak, longest streak, activity count, and today's activities

#### `GET /streaks/get-calendar-data`
- Returns calendar data for a specific month and year
- Optional activity type filter
- Includes activity status and streak count for each day

#### `GET /streaks/get-streaks`
- Returns all streaks for the current user
- Includes current streak, longest streak, and creation date for each activity type

#### `POST /streaks/log-activity`
- Logs a new activity
- Parameters: `activity_type`, `description` (optional)
- Updates streak calculations automatically

### Database Models

#### `Streak` Model
```python
class Streak(Base):
    __tablename__ = 'streaks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    activity_type = Column(String(50))  # e.g., 'coding', 'networking'
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
```

#### `StreakLog` Model
```python
class StreakLog(Base):
    __tablename__ = 'streak_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    activity_type = Column(String(50))
    activity_date = Column(DateTime, default=datetime.now)
    description = Column(String(200), nullable=True)
```

### Frontend Components

#### Calendar Grid
- CSS Grid layout with 7 columns (days of week)
- Responsive design that adapts to different screen sizes
- Interactive day cells with hover effects
- Color-coded activity indicators

#### Activity Form
- Dropdown for activity type selection
- Optional textarea for activity description
- Form validation and error handling
- Success/error message display

#### Statistics Cards
- Grid layout for displaying key metrics
- Large numbers with descriptive labels
- Color-coded for visual appeal

## Usage Instructions

### For Users

1. **Access the Streaks Page**
   - Navigate to `/streaks/page` (requires login)
   - Or click "View Full Calendar" from the home page sidebar

2. **Log an Activity**
   - Select an activity type from the dropdown
   - Optionally add a description
   - Click "Log Activity"

3. **View Your Progress**
   - Navigate through months using the arrow buttons
   - Click on any day to see details
   - Monitor your streaks in the statistics cards

4. **Track Different Activities**
   - Use the activity type filter to focus on specific activities
   - Build multiple streaks simultaneously
   - See overall progress across all activity types

### For Developers

1. **Database Setup**
   - Ensure the `streaks` and `streak_logs` tables exist
   - Run any necessary migrations

2. **API Testing**
   - Test endpoints with authentication
   - Verify streak calculation logic
   - Check calendar data generation

3. **Frontend Customization**
   - Modify activity types in the dropdowns
   - Adjust calendar styling and colors
   - Add new statistics or visual elements

## Customization Options

### Activity Types
The system supports custom activity types. To add new ones:

1. Update the dropdown options in `streaks.html`
2. Add the new type to the activity form
3. The backend will automatically handle new activity types

### Calendar Styling
- Modify CSS variables for colors and spacing
- Adjust calendar grid layout
- Customize day cell appearance
- Change hover effects and animations

### Statistics Display
- Add new metric cards
- Modify calculation logic
- Change visual presentation
- Add charts or graphs

## Browser Compatibility

- **Modern Browsers**: Chrome, Firefox, Safari, Edge (latest versions)
- **CSS Grid**: Required for calendar layout
- **JavaScript ES6+**: Required for async/await functionality
- **Responsive Design**: Works on mobile and desktop

## Performance Considerations

- **Database Queries**: Optimized with proper indexing
- **Caching**: Calendar data can be cached for better performance
- **Lazy Loading**: Calendar renders month by month
- **Efficient Updates**: Only refreshes necessary data after logging activities

## Future Enhancements

### Planned Features
- **Weekly View**: Alternative calendar layout
- **Goal Setting**: Set targets for specific activities
- **Social Features**: Share streaks with friends
- **Notifications**: Reminders for daily activities
- **Export Data**: Download streak history

### Technical Improvements
- **Real-time Updates**: WebSocket integration
- **Offline Support**: Service worker for offline functionality
- **Advanced Analytics**: Trend analysis and insights
- **Mobile App**: Native mobile application

## Troubleshooting

### Common Issues

1. **Calendar Not Loading**
   - Check browser console for JavaScript errors
   - Verify API endpoints are accessible
   - Ensure user is authenticated

2. **Activities Not Logging**
   - Check form validation
   - Verify API endpoint is working
   - Check database connection

3. **Streaks Not Calculating**
   - Verify activity dates are correct
   - Check streak calculation logic
   - Ensure database transactions are working

### Debug Information
- Check browser developer tools console
- Verify API responses in Network tab
- Check server logs for backend errors
- Test database queries directly

## Support

For technical support or feature requests:
- Check the API documentation at `/docs`
- Review server logs for error details
- Test individual endpoints for functionality
- Verify database schema and data integrity

---

**Note**: This feature requires user authentication and a working database connection. Make sure the user is logged in before accessing the streaks functionality.
