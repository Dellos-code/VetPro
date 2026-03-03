package com.vetpro.controller;

import com.vetpro.model.Reminder;
import com.vetpro.service.ReminderService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/reminders")
public class ReminderController {

    private final ReminderService reminderService;

    public ReminderController(ReminderService reminderService) {
        this.reminderService = reminderService;
    }

    @PostMapping
    public ResponseEntity<Reminder> createReminder(@Valid @RequestBody Reminder reminder) {
        Reminder created = reminderService.createReminder(reminder);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<List<Reminder>> getByUser(@PathVariable Long userId) {
        return ResponseEntity.ok(reminderService.getRemindersByUser(userId));
    }

    @GetMapping("/pending")
    public ResponseEntity<List<Reminder>> getPendingReminders() {
        return ResponseEntity.ok(reminderService.getPendingReminders());
    }

    @PutMapping("/{id}/sent")
    public ResponseEntity<Reminder> markAsSent(@PathVariable Long id) {
        return ResponseEntity.ok(reminderService.markAsSent(id));
    }
}
