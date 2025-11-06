import mongoose from 'mongoose';

const contactSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  email: {
    type: String,
    trim: true,
    lowercase: true
  },
  phone: {
    type: String,
    trim: true
  },
  company: {
    type: String,
    trim: true
  },
  notes: {
    type: String,
    trim: true
  },
  lastContact: {
    type: Date,
    default: Date.now
  },
  nextReminder: {
    type: Date
  },
  tags: [{
    type: String,
    trim: true
  }]
}, {
  timestamps: true
});

// Index for efficient querying
contactSchema.index({ user: 1, name: 1 });

export default mongoose.model('Contact', contactSchema);