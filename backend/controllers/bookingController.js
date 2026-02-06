const Booking = require('../models/Booking');

exports.checkAvailability = async (req, res) => {
    try {
        const { id } = req.params;
        const { startDate, endDate } = req.query;
        
        if (!startDate || !endDate) {
            return res.status(400).json({ 
                error: 'Start date and end date are required' 
            });
        }
        
        const isAvailable = await Booking.checkAvailability(id, startDate, endDate);
        
        res.json({ available: isAvailable });
        
    } catch (error) {
        console.error('Error checking availability:', error);
        res.status(500).json({ error: 'Server error' });
    }
};

exports.getBookedDates = async (req, res) => {
    try {
        const { id } = req.params;
        const bookedDates = await Booking.getBookedDates(id);
        
        res.json({ bookedDates });
        
    } catch (error) {
        console.error('Error fetching booked dates:', error);
        res.status(500).json({ error: 'Server error' });
    }
};

exports.createBooking = async (req, res) => {
    try {
        const { dress_id, start_date, end_date, total_price, security_deposit } = req.body;
        const renter_id = req.user.id; // From auth middleware
        
        // Validate dates
        if (new Date(start_date) >= new Date(end_date)) {
            return res.status(400).json({ 
                error: 'End date must be after start date' 
            });
        }
        
        const bookingId = await Booking.create({
            dress_id,
            renter_id,
            start_date,
            end_date,
            total_price,
            security_deposit
        });
        
        res.status(201).json({ 
            success: true, 
            bookingId,
            message: 'Booking created successfully' 
        });
        
    } catch (error) {
        if (error.message === 'Dates no longer available') {
            return res.status(409).json({ error: error.message });
        }
        console.error('Error creating booking:', error);
        res.status(500).json({ error: 'Failed to create booking' });
    }
};