import express from 'express';
import auth from '../middleware/auth.js';
import Contact from '../models/Contact.js';

const router = express.Router();

// Get all contacts for user
router.get('/', auth, async (req, res) => {
  try {
    const contacts = await Contact.find({ user: req.user._id }).sort({ name: 1 });
    res.json(contacts);
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Create new contact
router.post('/', auth, async (req, res) => {
  try {
    const contact = new Contact({
      ...req.body,
      user: req.user._id
    });

    await contact.save();
    res.status(201).json(contact);
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Update contact
router.put('/:id', auth, async (req, res) => {
  try {
    const contact = await Contact.findOneAndUpdate(
      { _id: req.params.id, user: req.user._id },
      { $set: req.body },
      { new: true }
    );

    if (!contact) {
      return res.status(404).json({ message: 'Contact not found' });
    }

    res.json(contact);
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Delete contact
router.delete('/:id', auth, async (req, res) => {
  try {
    const contact = await Contact.findOneAndDelete({
      _id: req.params.id,
      user: req.user._id
    });

    if (!contact) {
      return res.status(404).json({ message: 'Contact not found' });
    }

    res.json({ message: 'Contact deleted' });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;