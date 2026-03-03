package com.vetpro.service;

import com.vetpro.model.Reminder;
import com.vetpro.repository.ReminderRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional
public class ReminderService {

    private final ReminderRepository reminderRepository;

    public ReminderService(ReminderRepository reminderRepository) {
        this.reminderRepository = reminderRepository;
    }

    public Reminder createReminder(Reminder reminder) {
        return reminderRepository.save(reminder);
    }

    @Transactional(readOnly = true)
    public List<Reminder> getRemindersByUser(Long userId) {
        return reminderRepository.findByUserId(userId);
    }

    @Transactional(readOnly = true)
    public List<Reminder> getPendingReminders() {
        return reminderRepository.findBySentFalseAndReminderDateBefore(LocalDateTime.now());
    }

    public Reminder markAsSent(Long id) {
        Reminder reminder = reminderRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Reminder not found"));
        reminder.setSent(true);
        return reminderRepository.save(reminder);
    }
}
